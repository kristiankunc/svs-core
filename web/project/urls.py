import os

from web.project.settings import BASE_DIR

# import all urlpatterns from app.views modules dynamically
urlpatterns = []
for module_name in os.listdir(BASE_DIR / "app" / "views"):
    if module_name.endswith(".py") and module_name != "__init__.py":
        module_path = f"web.app.views.{module_name[:-3]}"
        module = __import__(module_path, fromlist=["urlpatterns"])
        if hasattr(module, "urlpatterns"):
            urlpatterns += module.urlpatterns
