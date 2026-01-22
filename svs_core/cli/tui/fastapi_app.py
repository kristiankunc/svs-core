"""Standalone FastAPI web server for SVS with session-based authentication.

This module provides a lightweight web interface for SVS using FastAPI.
Sessions are stored in-memory without database access.
Users can save login credentials in browser localStorage.
Sessions persist across page refreshes.
"""

import os
from pathlib import Path
from typing import Optional

import django
from django.apps import apps as django_apps

if not django_apps.ready:
    os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"
    django.setup()

from fastapi import FastAPI, Request, Response, HTTPException, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

from svs_core.users.user import User
from svs_core.cli.state import set_current_user
from svs_core.cli.tui.session_manager import get_session_manager

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "web_templates"
STATIC_DIR = BASE_DIR / "web_static"

# Ensure templates directory exists
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Create FastAPI app
app = FastAPI(title="SVS Web", version="0.1.0")

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def get_user_from_request(request: Request) -> Optional[dict]:
    """Extract user info from session cookie in request.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        Dictionary with user info if valid session, None otherwise
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        return None
    
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        return None
    
    try:
        user = User.objects.get(id=session.user_id)
        return {
            "user": user,
            "username": user.name,
            "is_admin": session.is_admin,
        }
    except User.DoesNotExist:
        session_manager.delete_session(session_id)
        return None


def require_login(request: Request) -> dict:
    """Dependency that requires authentication for protected routes.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        Dictionary with user info
        
    Raises:
        HTTPException: 403 if not authenticated
    """
    user_info = get_user_from_request(request)
    if not user_info:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return user_info


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main dashboard page."""
    user_info = get_user_from_request(request)
    
    if not user_info:
        return RedirectResponse(url="/login", status_code=303)
    
    context = {
        "request": request,
        "user": user_info["user"],
        "username": user_info["username"],
        "is_admin": user_info["is_admin"],
    }
    
    return templates.TemplateResponse("index.html", context)


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Display the login form."""
    user_info = get_user_from_request(request)
    
    # Redirect to dashboard if already logged in
    if user_info:
        return RedirectResponse(url="/", status_code=303)
    
    context = {"request": request, "error": None}
    return templates.TemplateResponse("login.html", context)


@app.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    """Process login credentials and create session."""
    # Check if already logged in
    user_info = get_user_from_request(request)
    if user_info:
        return RedirectResponse(url="/", status_code=303)
    
    # Validate input
    username = username.strip()
    if not username or not password:
        context = {
            "request": request,
            "error": "Username and password are required"
        }
        return templates.TemplateResponse("login.html", context, status_code=400)
    
    # Check credentials
    try:
        user = User.objects.get(name=username)
    except User.DoesNotExist:
        context = {
            "request": request,
            "error": "Invalid username or password"
        }
        return templates.TemplateResponse("login.html", context, status_code=401)
    
    if not user.check_password(password):
        context = {
            "request": request,
            "error": "Invalid username or password"
        }
        return templates.TemplateResponse("login.html", context, status_code=401)
    
    # Create session
    session_manager = get_session_manager()
    session_id = session_manager.create_session(
        user_id=user.id,
        username=user.name,
        is_admin=user.is_admin()
    )
    
    # Set CLI context for background operations
    set_current_user(user.name, user.is_admin())
    
    # Create response with session cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
        max_age=86400 * 7,  # 7 days
    )
    
    return response


@app.get("/logout")
async def logout(request: Request):
    """Logout and destroy session."""
    session_id = request.cookies.get("session_id")
    
    if session_id:
        session_manager = get_session_manager()
        session_manager.delete_session(session_id)
    
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response


@app.get("/api/user")
async def get_user_api(request: Request, user_info: dict = Depends(require_login)):
    """Get current user info as JSON."""
    return {
        "username": user_info["username"],
        "is_admin": user_info["is_admin"],
    }


@app.get("/api/check-session")
async def check_session(request: Request):
    """Check if user has a valid session (for keeping sessions alive on refresh)."""
    user_info = get_user_from_request(request)
    
    if not user_info:
        return JSONResponse({"authenticated": False}, status_code=401)
    
    return JSONResponse({
        "authenticated": True,
        "username": user_info["username"],
        "is_admin": user_info["is_admin"],
    })


def run_web_app(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI web application.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Whether to enable auto-reload on file changes
    """
    uvicorn.run(
        "svs_core.cli.tui.fastapi_app:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    run_web_app(reload=True)
