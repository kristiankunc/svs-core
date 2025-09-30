from django.shortcuts import render
from django.urls import path

from app.lib.user import get_user_if_authenticated
from web import settings


async def index(request):
    if settings.DEBUG:
        request.session["username"] = "testuser"
        request.session["is_authenticated"] = True
        request.session.set_expiry(3600)

    return render(
        request, "index.html", {"user": await get_user_if_authenticated(request)}
    )


views = [
    path("", index, name="index"),
]
