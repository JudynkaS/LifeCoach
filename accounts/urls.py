from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import SignUpView, ProfileUpdateView, profile_view, ProfileDetailView, google_oauth_start, google_oauth_callback, ClientDetailView, ClientListView  # removed client_intake

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='viewer:home'), name='logout'),
    path('register/', SignUpView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile_edit'),
    path('google-oauth/', google_oauth_start, name='google_oauth_start'),
    path('google-oauth-callback/', google_oauth_callback, name='google_oauth_callback'),
    path('client/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('', include('django.contrib.auth.urls')),
]
