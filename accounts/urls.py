from django.urls import path
from .views import SubmittableLoginView, user_logout, SignUpView, ProfileDetailView, ProfileUpdateView

app_name = 'accounts'

urlpatterns = [
    path('login/', SubmittableLoginView.as_view(), name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', SignUpView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),
] 