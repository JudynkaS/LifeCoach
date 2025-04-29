from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView
from django.contrib import messages

from accounts.forms import SignUpForm, ProfileUpdateForm
from accounts.models import Profile
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


class SubmittableLoginView(LoginView):
    template_name = 'registration/login.html'


class SignUpView(CreateView):
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('viewer:home')


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))  # zůstat na stejné stránce


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

@login_required
def profile_view(request):
    profile = getattr(request.user, 'profile', None)
    return render(request, 'accounts/profile.html', {'profile': profile, 'user': request.user})