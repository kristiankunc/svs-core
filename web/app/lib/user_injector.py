from svs_core.users.user import User


def user_render_injector(request):
    user_id = request.session.get("user_id")
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass

    return {"user": user}
