from django.http import HttpRequest


def is_owner_or_admin(request: HttpRequest, model: object) -> bool:
    """Check if the current user is the owner of the object or an admin."""
    user_id = request.session.get("user_id")
    is_admin = request.session.get("is_admin", False)

    if is_admin:
        return True

    if user_id and hasattr(model, "user"):
        return model.user.id == user_id

    return False
