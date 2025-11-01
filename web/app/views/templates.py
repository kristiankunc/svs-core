from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path

from svs_core.docker.template import Template
from web.app.lib.owner_check import is_owner_or_admin
from web.app.views.base import render


def list(request: HttpRequest):
    templates = Template.objects.all()
    return render(request, "templates/list.html", {"templates": templates})


def detail(request: HttpRequest, template_id: int):
    template = Template.objects.get(id=template_id)
    return render(request, "templates/detail.html", {"template": template})


def delete(request: HttpRequest, template_id: int):
    template = Template.objects.get(id=template_id)

    print(f"Attempting to delete template with ID {template_id}")
    print(f"is_owner_or_admin: {is_owner_or_admin(request, template)}")

    if is_owner_or_admin(request, template):
        try:
            template.delete()
            messages.success(request, "Template deleted successfully.")
        except Exception as e:
            print(f"Error deleting template: {e}")
            messages.error(request, f"Error deleting template: {e}")

    return redirect("list_templates")


urlpatterns = [
    path("templates/", list, name="list_templates"),
    path("templates/<int:template_id>/", detail, name="detail_template"),
    path("templates/<int:template_id>/delete/", delete, name="delete_template"),
]
