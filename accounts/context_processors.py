from .models import Profile

def user_profile(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
    # Najdi profil kouče
    coach_profile = Profile.objects.filter(is_coach=True).first()
    return {'profile': profile, 'coach_profile': coach_profile} 