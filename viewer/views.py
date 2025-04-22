from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse
from accounts.forms import UserRegistrationForm
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = "viewer/home.html"  # ← Tohle je klíč



class RegisterView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # automatické přihlášení po registraci
        return response

    def get_success_url(self):
        if self.object.is_coach:
            return reverse('coach_dashboard')
        return reverse('client_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')  # nebo jiná logika
        return super().dispatch(request, *args, **kwargs)
