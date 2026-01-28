"""Models module for svs_core app.

This module imports all models from svs_core.db.models to ensure Django
can properly locate them for migrations and other operations.
"""

from svs_core.db.models import (  # noqa: F401
    GitSourceModel,
    ServiceModel,
    TemplateModel,
    UserGroupModel,
    UserModel,
)

# Set the __module__ attribute so Django sees these models as belonging to svs_core.models
# This is necessary because the models are actually defined in svs_core.db.models
UserModel.__module__ = "svs_core.models"
TemplateModel.__module__ = "svs_core.models"
ServiceModel.__module__ = "svs_core.models"
GitSourceModel.__module__ = "svs_core.models"
UserGroupModel.__module__ = "svs_core.models"

__all__ = [
    "UserModel",
    "TemplateModel",
    "ServiceModel",
    "GitSourceModel",
    "UserGroupModel",
]
