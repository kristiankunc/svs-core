import json

from pathlib import Path

import requests

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

VITE_DEV_SERVER = "http://127.0.0.1:5173"
VITE_FALLBACK_URL = "http://127.0.0.1:8000"
MANIFEST_PATH = Path(settings.BASE_DIR) / "static/vite/.vite/manifest.json"


def _dev_server_running():
    """Check if Vite dev server is running."""
    try:
        response = requests.head(VITE_DEV_SERVER, timeout=1)
        is_running = response.status_code < 500
        return is_running
    except (requests.ConnectionError, requests.Timeout) as e:
        return False


def _load_manifest():
    """Load and cache manifest.json."""
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return None


def _html_tag(tag_type, src):
    """Generate HTML tag for asset."""
    if tag_type == "css":
        return mark_safe(f'<link rel="stylesheet" href="{src}">')
    return mark_safe(f'<script type="module" src="{src}"></script>')


@register.simple_tag
def vite(file_type="js"):
    """Load Vite assets (JS or CSS)

    Prefers dev server in development mode, falls back to built assets
    or Django static files.
    """
    if not settings.DEBUG:
        manifest = _load_manifest()
        if manifest:
            entry = manifest.get("src/main.js")
            if entry:
                if file_type == "css":
                    css_files = entry.get("css", [])
                    if css_files:
                        css_path = static(f"vite/{css_files[0]}")
                        return _html_tag("css", css_path)
                else:
                    js_path = static(f"vite/{entry['file']}")
                    return _html_tag("js", js_path)
        return ""

    dev_running = _dev_server_running()

    if dev_running:
        if file_type == "js":
            src = f"{VITE_DEV_SERVER}/src/main.js"
            return _html_tag("js", src)
        elif file_type == "css":
            return ""
    else:
        manifest = _load_manifest()
        if manifest:
            entry = manifest.get("src/main.js")
            if entry:
                if file_type == "css":
                    css_files = entry.get("css", [])
                    if css_files:
                        css_path = static(f"vite/{css_files[0]}")
                        return _html_tag("css", css_path)
                else:
                    js_path = static(f"vite/{entry['file']}")
                    return _html_tag("js", js_path)

        if file_type == "js":
            src = f"{VITE_FALLBACK_URL}/static/vite/src/main.js"
            return _html_tag("js", src)
        elif file_type == "css":
            src = f"{VITE_FALLBACK_URL}/static/vite/style.css"
            return _html_tag("css", src)

    return ""


@register.simple_tag
def vite_hmr():
    """Load Vite HMR client in development mode."""
    if settings.DEBUG and _dev_server_running():
        return mark_safe(
            f'<script type="module" src="{VITE_DEV_SERVER}/@vite/client"></script>'
        )
    return ""
