import json

from pathlib import Path

from django import template
from django.conf import settings
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

# dev server URL must match what you run
VITE_DEV_URL = "http://127.0.0.1:5173"


@register.simple_tag
def vite(file_type="js"):
    if settings.DEBUG:
        # In development, return the dev server entry point
        if file_type == "js":
            return "http://127.0.0.1:5173/src/main.js"
        # No CSS in dev mode - Vite injects it via JS
        return ""

    # production: manifest
    manifest_path = Path(settings.BASE_DIR) / "static/vite/.vite/manifest.json"
    if not manifest_path.exists():
        return ""
    with open(manifest_path) as f:
        data = json.load(f)
    entry = data.get("src/main.js")
    if not entry:
        return ""
    if file_type == "css":
        css_files = entry.get("css")
        if css_files:
            return static(f"vite/{css_files[0]}")
        return ""
    return static(f"vite/{entry['file']}")


@register.simple_tag
def vite_hmr():
    """Load Vite HMR client in development mode"""
    if settings.DEBUG:
        return mark_safe(
            f'<script type="module" src="{VITE_DEV_URL}/@vite/client"></script>'
        )
    return ""
