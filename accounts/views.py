from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from accounts.forms import SignUpForm, ProfileUpdateForm
from accounts.models import Profile

class SubmittableLoginView(LoginView):
    template_name = 'form.html'


class SignUpView(CreateView):
    template_name = 'form.html'
    form_class = SignUpForm
    success_url = reverse_lazy('home')


def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))  # zůstat na stejné stránce


class ProfileDetailView(DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'form.html'
    
    def get_success_url(self):
        return reverse_lazy('accounts:profile', kwargs={'pk': self.object.pk})
    
    def get_object(self, queryset=None):
        return self.request.user.profile