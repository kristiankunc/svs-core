from app.lib.user import get_user_if_authenticated
from django.http import Http404
from django.shortcuts import render
from django.urls import path

from svs_core.docker.template import Template


async def instantiate_template(request, template_id: int):
    if request.method != "POST":
        template = await Template.get_by_id(template_id)

        if not template:
            raise Http404("Template not found")

        return render(
            request,
            "service/instantiate_template.html",
            {"user": await get_user_if_authenticated(request), "template": template},
        )


views = [
    path(
        "service/instantiate_template/<int:template_id>/",
        instantiate_template,
        name="instantiate_template",
    ),
]
