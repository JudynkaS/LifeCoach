from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db.models import Q

from accounts.forms import SignUpForm
from .models import Session, Service
from .forms import ServiceForm

class HomeView(TemplateView):
    template_name = "viewer/home.html"


class RegisterView(CreateView):
    form_class = SignUpForm
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


class SessionHistoryView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'viewer/session_history.html'
    context_object_name = 'sessions'
    paginate_by = 10

    def get_queryset(self):
        user_profile = self.request.user.profile
        if user_profile.is_coach:
            return Session.objects.filter(coach=user_profile).order_by('-date_time')
        else:
            return Session.objects.filter(client=user_profile).order_by('-date_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = self.request.user.profile
        
        # Add upcoming and past sessions
        if user_profile.is_coach:
            context['upcoming_sessions'] = Session.objects.filter(
                coach=user_profile,
                date_time__gt=timezone.now(),
                status='CONFIRMED'
            ).order_by('date_time')
            context['past_sessions'] = Session.objects.filter(
                coach=user_profile,
                date_time__lte=timezone.now()
            ).order_by('-date_time')
        else:
            context['upcoming_sessions'] = Session.objects.filter(
                client=user_profile,
                date_time__gt=timezone.now(),
                status='CONFIRMED'
            ).order_by('date_time')
            context['past_sessions'] = Session.objects.filter(
                client=user_profile,
                date_time__lte=timezone.now()
            ).order_by('-date_time')
        
        return context


class SessionDetailView(LoginRequiredMixin, DetailView):
    model = Session
    template_name = 'viewer/session_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        user_profile = self.request.user.profile
        if user_profile.is_coach:
            return Session.objects.filter(coach=user_profile)
        else:
            return Session.objects.filter(client=user_profile)


class ServiceListView(ListView):
    model = Service
    template_name = 'viewer/service_list.html'
    context_object_name = 'services'

    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True)
        if self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
            if self.request.user.profile.is_coach:
                # Coaches see only their services
                return queryset.filter(coach=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_coach'] = self.request.user.is_authenticated and hasattr(self.request.user, 'profile') and self.request.user.profile.is_coach
        return context


class ServiceDetailView(DetailView):
    model = Service
    template_name = 'viewer/service_detail.html'
    context_object_name = 'service'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['is_coach'] = hasattr(self.request.user, 'profile') and self.request.user.profile.is_coach
            if not context['is_coach']:
                # For clients, show available time slots
                # This is a placeholder - you'll need to implement the actual logic
                context['available_slots'] = []
        return context


class ServiceCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = 'viewer/service_form.html'
    success_url = reverse_lazy('viewer:services')

    def test_func(self):
        return hasattr(self.request.user, 'profile') and self.request.user.profile.is_coach

    def form_valid(self, form):
        form.instance.coach = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Service'
        context['button_text'] = 'Create Service'
        return context


class ServiceUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = 'viewer/service_form.html'
    success_url = reverse_lazy('viewer:services')

    def test_func(self):
        service = self.get_object()
        return self.request.user == service.coach

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Service'
        context['button_text'] = 'Update Service'
        return context


class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Service
    template_name = 'viewer/service_confirm_delete.html'
    success_url = reverse_lazy('viewer:services')

    def test_func(self):
        service = self.get_object()
        return self.request.user == service.coach
