from pathlib import Path

from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path
from django.utils.timezone import now

from app.lib.owner_check import is_owner_or_admin
from svs_core.docker.json_properties import EnvVariable, ExposedPort, Label, Volume
from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.shared.git_source import GitSource
from svs_core.shared.logger import get_logger
from svs_core.users.user import User


def create_from_template(request: HttpRequest, template_id: int):
    """Display form to create a service from a template."""
    template = get_object_or_404(Template, id=template_id)

    if request.method == "POST":
        service_name = request.POST.get("name", "")
        domain = request.POST.get("domain", "")

        user_id = request.session.get("user_id")
        if not user_id:
            return redirect("login")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return redirect("login")

        override_env = []
        env_keys = request.POST.getlist("env_key[]")
        env_values = request.POST.getlist("env_value[]")
        for key, value in zip(env_keys, env_values):
            override_env.append(EnvVariable(key=key, value=value))

        override_ports = []
        port_host = request.POST.getlist("port_host[]")
        port_container = request.POST.getlist("port_container[]")
        for host, container in zip(port_host, port_container):
            override_ports.append(
                ExposedPort(
                    host_port=int(host) if host else None,
                    container_port=int(container) if container else None,
                )
            )

        override_volumes = []
        vol_host = request.POST.getlist("volume_host[]")
        vol_container = request.POST.getlist("volume_container[]")
        for host, container in zip(vol_host, vol_container):
            override_volumes.append(
                Volume(host_path=host if host else None, container_path=container)
            )

        # Parse git sources
        git_source_urls = request.POST.getlist("git_source_url[]")
        git_source_branches = request.POST.getlist("git_source_branch[]")
        git_source_paths = request.POST.getlist("git_source_path[]")

        try:
            service = Service.create_from_template(
                name=service_name,
                template_id=template_id,
                user=user,
                domain=domain if domain else None,
                override_env=override_env if override_env else None,
                override_ports=override_ports if override_ports else None,
                override_volumes=override_volumes if override_volumes else None,
            )

            # Create git sources after service creation
            for url, branch, path in zip(
                git_source_urls, git_source_branches, git_source_paths
            ):
                if url and path:  # Only create if both URL and path are provided
                    GitSource.create(
                        service_id=service.id,
                        repository_url=url,
                        destination_path=Path(path),
                        branch=branch if branch else "main",
                    )

            return redirect("detail_service", service_id=service.id)
        except Exception as e:
            return render(
                request,
                "services/create_from_template.html",
                {
                    "template": template,
                    "error": str(e),
                },
            )

    return render(
        request,
        "services/create_from_template.html",
        {
            "template": template,
        },
    )


def detail(request: HttpRequest, service_id: int):
    """Display service details."""
    service = get_object_or_404(Service, id=service_id)
    return render(request, "services/detail.html", {"service": service})


def list_services(request: HttpRequest):
    """List all services."""
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin", False)

    if is_admin:
        services = Service.objects.all()
    elif user_id:
        try:
            user = User.objects.get(id=user_id)
            services = user.proxy_services
        except User.DoesNotExist:
            services = []
    else:
        services = []

    return render(request, "services/list.html", {"services": services})


def start(request: HttpRequest, service_id: int):
    """Start a service."""
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    service.start()
    return redirect("detail_service", service_id=service.id)


def stop(request: HttpRequest, service_id: int):
    """Stop a service."""
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    service.stop()
    return redirect("detail_service", service_id=service.id)


def restart(request: HttpRequest, service_id: int):
    """Restart a service."""
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    service.stop()
    service.start()
    return redirect("detail_service", service_id=service.id)


def delete(request: HttpRequest, service_id: int):
    """Delete a service."""
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    service.delete()
    return redirect("list_services")


def view_logs(request: HttpRequest, service_id: int):
    """View service logs.

    Returns JSON if Accept header contains 'application/json', otherwise
    HTML.
    """
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    try:
        logs = service.get_logs()
    except Exception as e:
        logs = f"Error fetching logs: {str(e)}"

    # Check if client wants JSON
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header:
        return JsonResponse(
            {
                "success": True,
                "logs": logs,
                "timestamp": now().isoformat(),
            }
        )

    # Return HTML
    return render(request, "services/logs.html", {"service": service, "logs": logs})


def download_git_source(request: HttpRequest, service_id: int, git_source_id: int):
    """Download or update a git source for a service."""
    service = get_object_or_404(Service, id=service_id)
    git_source = get_object_or_404(GitSource, id=git_source_id, service_id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    try:
        git_source.download()
    except Exception as e:
        get_logger(__name__).error(
            f"Failed to download git source {git_source_id} for service {service_id}: {str(e)}"
        )
        return render(
            request,
            "services/detail.html",
            {"service": service, "error": f"Failed to download git source: {str(e)}"},
        )

    return redirect("detail_service", service_id=service.id)


def attach_git_source(request: HttpRequest, service_id: int):
    """Attach a git source to an existing service."""
    service = get_object_or_404(Service, id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    if request.method == "POST":
        git_url = request.POST.get("git_source_url", "").strip()
        git_branch = request.POST.get("git_source_branch", "main").strip()
        git_path = request.POST.get("git_source_path", "").strip()

        if not git_url or not git_path:
            return render(
                request,
                "services/detail.html",
                {
                    "service": service,
                    "error": "Git URL and destination path are required.",
                },
            )

        try:
            git_path_obj = Path(git_path)
            service.add_git_source(git_url, git_branch, git_path_obj)
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to attach git source to service {service_id}: {str(e)}"
            )
            return render(
                request,
                "services/detail.html",
                {"service": service, "error": f"Failed to attach git source: {str(e)}"},
            )

        return redirect("detail_service", service_id=service.id)

    return render(request, "services/detail.html", {"service": service})


def delete_git_source(request: HttpRequest, service_id: int, git_source_id: int):
    """Delete a git source from a service."""
    service = get_object_or_404(Service, id=service_id)
    git_source = get_object_or_404(GitSource, id=git_source_id, service_id=service_id)

    if not is_owner_or_admin(request, service):
        return redirect("detail_service", service_id=service.id)

    try:
        git_source.delete()
    except Exception as e:
        get_logger(__name__).error(
            f"Failed to delete git source {git_source_id} from service {service_id}: {str(e)}"
        )
        return render(
            request,
            "services/detail.html",
            {"service": service, "error": f"Failed to delete git source: {str(e)}"},
        )

    return redirect("detail_service", service_id=service.id)


urlpatterns = [
    path("services/", list_services, name="list_services"),
    path(
        "services/create/<int:template_id>/",
        create_from_template,
        name="create_service_from_template",
    ),
    path("services/<int:service_id>/", detail, name="detail_service"),
    path("services/<int:service_id>/start/", start, name="start_service"),
    path("services/<int:service_id>/stop/", stop, name="stop_service"),
    path("services/<int:service_id>/restart/", restart, name="restart_service"),
    path("services/<int:service_id>/delete/", delete, name="delete_service"),
    path("services/<int:service_id>/logs/", view_logs, name="view_service_logs"),
    path(
        "services/<int:service_id>/git-sources/attach/",
        attach_git_source,
        name="attach_git_source",
    ),
    path(
        "services/<int:service_id>/git-sources/<int:git_source_id>/download/",
        download_git_source,
        name="download_git_source",
    ),
    path(
        "services/<int:service_id>/git-sources/<int:git_source_id>/delete/",
        delete_git_source,
        name="delete_git_source",
    ),
]
