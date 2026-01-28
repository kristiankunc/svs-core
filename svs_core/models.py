"""Models module for svs_core app.

This module imports all models from svs_core.db.models to ensure Django
can properly locate them for migrations and other operations.
"""

# Re-export models from svs_core.db.models
# This allows Django to find the models module while keeping the models
# in their original location to maintain migration compatibility
from svs_core.db.models import (  # noqa: F401
    GitSourceModel,
    ServiceModel,
    TemplateModel,
    UserGroupModel,
    UserModel,
)

__all__ = [
    "UserModel",
    "TemplateModel",
    "ServiceModel",
    "GitSourceModel",
    "UserGroupModel",
]
