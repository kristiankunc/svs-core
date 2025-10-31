from svs_core.users.user import User


def user_render_injector(request):
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            is_admin = user.is_admin()
        except User.DoesNotExist:
            pass

    return {"user": user, "is_admin": is_admin}
