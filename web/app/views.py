from django.http import Http404
from django.shortcuts import redirect, render

from svs_core.docker.template import Template
from svs_core.users.user import User
from web import settings


async def index(request):
    if settings.DEBUG:
        request.session["username"] = "testuser"
        request.session["is_authenticated"] = True
        request.session.set_expiry(3600)

    user = None
    if request.session.get("is_authenticated", False):
        user = await User.get_by_name(request.session["username"])

    print(f"Session: {request.session.items()}", flush=True)

    print(f"User: {user}", flush=True)

    return render(request, "index.html", {"user": user})


async def login(request):
    if request.method != "POST":
        return render(request, "login.html", {})

    else:
        username = request.POST.get("username")
        password = request.POST.get("password")

        print(f"Username: {username}, Password: {password}")

        user = await User.get_by_name(username)

        if user and await user.check_password(password):
            request.session["username"] = username
            request.session["is_authenticated"] = True
            request.session.set_expiry(3600)
            return redirect("index")
        else:
            return render(
                request, "login.html", {"error": "Invalid username or password"}
            )


def logout(request):
    request.session.flush()
    return redirect("index")


async def templates(request):
    user = None
    if request.session.get("is_authenticated", False):
        user = await User.get_by_name(request.session["username"])
    templates = await Template.get_all()
    return render(request, "templates.html", {"templates": templates, "user": user})


async def template_detail(request, template_id):
    try:
        user = None
        if request.session.get("is_authenticated", False):
            user = await User.get_by_name(request.session["username"])
        template = await Template.get_by_id(template_id)
        if not template:
            raise Http404("Template not found")
        return render(
            request, "template_detail.html", {"template": template, "user": user}
        )
    except Exception as e:
        raise Http404(f"Template not found: {e}")
