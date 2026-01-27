import json

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import path

from app.lib.owner_check import is_owner_or_admin
from app.views.base import render
from svs_core.docker.template import Template
from svs_core.users.user import User


def list(request: HttpRequest):
    """List templates - accessible to all users (authenticated or not)."""
    templates = Template.objects.all()
    return render(request, "templates/list.html", {"templates": templates})


def detail(request: HttpRequest, template_id: int):
    """View template details - accessible to all users (authenticated or not)."""
    template = Template.objects.get(id=template_id)
    return render(request, "templates/detail.html", {"template": template})


def import_from_json(request: HttpRequest):
    """Import a template from JSON - only authenticated users can do this."""
    # Check if user is authenticated
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

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
    """Delete a template - only admins can delete templates."""
    # Check if user is admin
    is_admin = request.session.get("is_admin", False)
    if not is_admin:
        messages.error(request, "You don't have permission to delete templates.")
        return redirect("list_templates")

    template = Template.objects.get(id=template_id)

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
