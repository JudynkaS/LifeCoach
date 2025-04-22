from django.urls import path
from accounts.views import RegisterView, ProfileDetailView, SubmittableLoginView, user_logout

app_name = 'accounts'

urlpatterns = [
    path('login/', SubmittableLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileDetailView.as_view(), name='profile'),
] 