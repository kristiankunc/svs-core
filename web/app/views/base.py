from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import path
from project.settings import DEBUG

from svs_core.users.user import User


def index(request):
    return render(request, "base/index.html")


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
            return redirect("index")

    return render(request, "base/login.html", {"error": "Invalid credentials"})


def logout(request: HttpRequest):
    request.session.flush()
    return redirect("index")


urlpatterns = [
    path("", index, name="index"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
