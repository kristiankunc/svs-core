import json

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path

from app.lib.owner_check import is_owner_or_admin
from app.views.base import render
from svs_core.docker.template import Template


def list(request: HttpRequest):
    templates = Template.objects.all()
    return render(request, "templates/list.html", {"templates": templates})


def detail(request: HttpRequest, template_id: int):
    template = Template.objects.get(id=template_id)
    return render(request, "templates/detail.html", {"template": template})


def import_from_json(request: HttpRequest):
    if request.method == "POST":
        json_data = request.POST.get("json_data", "")
        try:
            data = json.loads(json_data)
            template = Template.import_from_json(data)
            messages.success(request, "Template imported successfully.")
        except json.JSONDecodeError as e:
            messages.error(request, f"Invalid JSON format: {e}")
            return redirect("import_template")
        except Exception as e:
            messages.error(request, f"Error importing template: {e}")
            return redirect("import_template")

        return redirect("detail_template", template_id=template.id)

    return render(request, "templates/import.html")


def delete(request: HttpRequest, template_id: int):
    template = Template.objects.get(id=template_id)

    if is_owner_or_admin(request, template):
        try:
            template.delete()
            messages.success(request, "Template deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting template: {e}")

    return redirect("list_templates")


urlpatterns = [
    path("templates/", list, name="list_templates"),
    path("templates/<int:template_id>/", detail, name="detail_template"),
    path("templates/import/", import_from_json, name="import_template"),
    path("templates/<int:template_id>/delete/", delete, name="delete_template"),
]
