from app.lib.user import get_user_if_authenticated
from django.http import Http404
from django.shortcuts import render
from django.urls import path

from svs_core.docker.template import Template


async def templates(request):
    templates = await Template.get_all()

    return render(
        request,
        "template/templates.html",
        {"templates": templates, "user": await get_user_if_authenticated(request)},
    )


async def template_detail(request, template_id):
    try:
        template = await Template.get_by_id(template_id)
        if not template:
            raise Http404("Template not found")

        return render(
            request,
            "template/template_detail.html",
            {"template": template, "user": await get_user_if_authenticated(request)},
        )
    except Exception as e:
        raise Http404(f"Template not found: {e}")


views = [
    path("templates/", templates, name="templates"),
    path("templates/<int:template_id>/", template_detail, name="template_detail"),
]
