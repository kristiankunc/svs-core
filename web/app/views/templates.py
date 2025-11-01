from django.http import HttpRequest
from django.urls import path

from svs_core.docker.template import Template
from web.app.views.base import render


def list(request: HttpRequest):
    templates = Template.objects.all()
    return render(request, "templates/list.html", {"templates": templates})


def detail(request: HttpRequest, template_id: int):
    template = Template.objects.get(id=template_id)
    return render(request, "templates/detail.html", {"template": template})


urlpatterns = [
    path("templates/", list, name="list_templates"),
    path("templates/<int:template_id>/", detail, name="detail_template"),
]
