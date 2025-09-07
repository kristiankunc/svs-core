from django.shortcuts import redirect, render

from svs_core.users.user import User


async def index(request):
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
