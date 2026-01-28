from django.apps import AppConfig


class SvsCoreConfig(AppConfig):  # type: ignore[misc] # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "svs_core"
