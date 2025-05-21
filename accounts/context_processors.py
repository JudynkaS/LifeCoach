from .models import Profile


def user_profile(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    return {"profile": profile}
