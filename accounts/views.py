from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.forms import UserRegistrationForm
from accounts.models import Profile

# Create your views here.

class SubmittableLoginView(LoginView):
    template_name = 'form.html'

class RegisterView(CreateView):
    template_name = 'form.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('viewer:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

def user_logout(request):
    logout(request)
    return redirect(request.META.get('HTTP_REFERER', '/'))

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'accounts/profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        return self.request.user.profile
