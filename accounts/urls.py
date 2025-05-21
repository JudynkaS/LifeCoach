from django.urls import path, include, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
    SignUpView,
    ProfileDetailView,
    google_oauth_start,
    google_oauth_callback,
    ClientDetailView,
    ClientListView,
    about_me,
    profile_edit,
)

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/", auth_views.LogoutView.as_view(next_page="viewer:home"), name="logout"
    ),
    path("register/", SignUpView.as_view(), name="register"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile"),
    path("profile/edit/", profile_edit, name="profile_edit"),
    path("google-oauth/", google_oauth_start, name="google_oauth_start"),
    path("google-oauth-callback/", google_oauth_callback, name="google_oauth_callback"),
    path("client/<int:pk>/", ClientDetailView.as_view(), name="client_detail"),
    path("clients/", ClientListView.as_view(), name="client_list"),
    path("about-me/", about_me, name="about_me"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change.html",
            success_url=reverse_lazy("accounts:password_change_done"),
        ),
        name="password_change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password_change_done",
    ),
]
