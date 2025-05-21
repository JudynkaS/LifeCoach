from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib import messages
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required

from accounts.forms import SignUpForm, ProfileUpdateForm, ClientProfileUpdateForm
from accounts.models import Profile

# Google OAuth2 imports
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Path to your credentials.json
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(
    settings.BASE_DIR, "config", "credentials.json"
)
GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


class SubmittableLoginView(LoginView):
    template_name = "registration/login.html"


class SignUpView(CreateView):
    template_name = "registration/register.html"
    form_class = SignUpForm
    success_url = reverse_lazy("viewer:home")


def user_logout(request):
    logout(request)
    return redirect(request.META.get("HTTP_REFERER", "/"))  # zůstat na stejné stránce


class CreateProfileView(LoginRequiredMixin, CreateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_create.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_client = True
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.object.pk})


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "accounts/profile.html"
    context_object_name = "profile"

    def get_object(self, queryset=None):
        return Profile.objects.get(pk=self.kwargs['pk'])


@login_required
def profile_edit(request):
    profile = request.user.profile
    if profile.is_coach:
        form_class = ProfileUpdateForm
        template = "accounts/profile_edit_coach.html"
    else:
        form_class = ClientProfileUpdateForm
        template = "accounts/profile_edit_client.html"
    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=profile)
        print("POST data:", request.POST)
        print("FILES:", request.FILES)
        if form.is_valid():
            print("Form is valid. Cleaned data:", form.cleaned_data)
            form.save()
            print("Profile saved successfully.")
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile", pk=profile.pk)
        else:
            print("Form errors:", form.errors)
    else:
        form = form_class(instance=profile)
    return render(request, template, {"form": form, "user": request.user})


@login_required
def google_oauth_start(request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=request.build_absolute_uri(
            reverse("accounts:google_oauth_callback")
        ),
    )
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    request.session["google_oauth_state"] = state
    return redirect(authorization_url)


@login_required
def google_oauth_callback(request):
    # Povolení OAuth2 přes HTTP v development módu
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    state = request.session.get("google_oauth_state")
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(
            reverse("accounts:google_oauth_callback")
        ),
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    refresh_token = credentials.refresh_token
    if not refresh_token:
        messages.error(
            request, "Failed to obtain Google refresh token. Please try again."
        )
        return redirect("accounts:profile_edit")
    # Ulož refresh token do profilu
    profile = request.user.profile
    profile.google_refresh_token = refresh_token
    profile.save()
    messages.success(request, "Google Calendar successfully connected!")
    return redirect("accounts:profile_edit")


class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/client_detail.html"
    context_object_name = "profile"

    def get_queryset(self):
        # Jen kouč může zobrazit detail klienta
        return Profile.objects.filter(is_client=True)


class ClientListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = "accounts/client_list.html"
    context_object_name = "clients"

    def get_queryset(self):
        return Profile.objects.filter(is_client=True)


def about_me(request):
    coach = Profile.objects.filter(is_coach=True).first()
    return render(request, "accounts/about_me.html", {"coach": coach})
