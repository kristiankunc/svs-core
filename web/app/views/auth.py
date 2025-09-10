from django.shortcuts import redirect, render
from django.urls import path

from svs_core.users.user import User


async def login(request):
    if request.method != "POST":
        return render(request, "auth/login.html", {})

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
                request, "auth/login.html", {"error": "Invalid username or password"}
            )


def logout(request):
    request.session.flush()
    return redirect("index")


views = [
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
]
