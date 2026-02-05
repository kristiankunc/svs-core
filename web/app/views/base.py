import logging

from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from django_ratelimit.decorators import ratelimit
from project.settings import DEBUG

from svs_core.users.user import User

security_logger = logging.getLogger("security")


def index(request):
    return render(request, "base/index.html")


@ratelimit(key="ip", rate="5/15m", method="POST", block=True)
def login(request: HttpRequest):

    if not request.method == "POST":
        return render(request, "base/login.html")

    username = request.POST.get("username")
    password = request.POST.get("password")

    if username and password:
        try:
            user = User.objects.get(name=username)
        except User.DoesNotExist:
            user = None

        if user and user.check_password(password):
            request.session["user_id"] = user.id
            request.session["is_admin"] = user.is_admin()
            security_logger.info(
                f"Successful login for user '{username}' from IP {request.META.get('REMOTE_ADDR')}"
            )
            return redirect("index")

    # Log failed login attempt without revealing whether username exists
    ip_address = request.META.get("REMOTE_ADDR")
    security_logger.warning(
        f"Failed login attempt from IP {ip_address} (username attempt: {username[:3] + '***' if username and len(username) > 3 else '***'})"
    )
    return render(request, "base/login.html", {"error": "Invalid credentials"})


def logout(request: HttpRequest):
    request.session.flush()
    return redirect("index")


urlpatterns = [
    path("", index, name="index"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
