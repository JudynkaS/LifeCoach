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

from accounts.forms import SignUpForm, ProfileUpdateForm
from accounts.models import Profile

# Google OAuth2 imports
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Path to your credentials.json
GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'config', 'credentials.json')
GOOGLE_SCOPES = ['https://www.googleapis.com/auth/calendar.events']

class SubmittableLoginView(LoginView):
    template_name = 'registration/login.html'


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))  # zůstat na stejné stránce


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
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return Profile.objects.get(pk=self.kwargs['pk'])


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        import logging
        logger = logging.getLogger(__name__)
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Profile updated successfully!')
            logger.info(f"Profile for user {self.request.user.username} updated successfully.")
            if self.request.FILES:
                logger.info(f"Uploaded files: {self.request.FILES}")
            if self.object.avatar:
                logger.info(f"Avatar path: {self.object.avatar.path}")
            return response
        except Exception as e:
            messages.error(self.request, f'Error updating profile: {str(e)}')
            logger.error(f"Error updating profile for user {self.request.user.username}: {str(e)}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('accounts:profile', kwargs={'pk': self.request.user.profile.pk})

@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/profile.html', {'profile': profile, 'user': request.user})

@login_required
def google_oauth_start(request):
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('accounts:google_oauth_callback')),
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    request.session['google_oauth_state'] = state
    return redirect(authorization_url)

@login_required
def google_oauth_callback(request):
    # Povolení OAuth2 přes HTTP v development módu
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    state = request.session.get('google_oauth_state')
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=GOOGLE_SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('accounts:google_oauth_callback')),
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials
    refresh_token = credentials.refresh_token
    if not refresh_token:
        messages.error(request, 'Failed to obtain Google refresh token. Please try again.')
        return redirect('accounts:profile_edit')
    # Ulož refresh token do profilu
    profile = request.user.profile
    profile.google_refresh_token = refresh_token
    profile.save()
    messages.success(request, 'Google Calendar successfully connected!')
    return redirect('accounts:profile_edit')

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/client_detail.html'
    context_object_name = 'profile'
    
    def get_queryset(self):
        # Jen kouč může zobrazit detail klienta
        return Profile.objects.filter(is_client=True)

class ClientListView(LoginRequiredMixin, ListView):
    model = Profile
    template_name = 'accounts/client_list.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Profile.objects.filter(is_client=True)

def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('viewer:home')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})