from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import SignUpView, ProfileUpdateView, profile_view  # removed client_intake

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='viewer:home'), name='logout'),
    path('register/', SignUpView.as_view(), name='register'),
    path('profile/', profile_view, name='profile'),  # TADY PŘEPNUTO na funkci
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('', include('django.contrib.auth.urls')),
]
