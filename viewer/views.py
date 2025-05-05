from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
<<<<<<< HEAD
from django.contrib import messages
from django.contrib.auth.models import User

from .models import Session, Service, Profile, Review
from .forms import ServiceForm, BookingForm
from .utils.google_calendar import create_psychology_session
=======
from django.db.models import Q

from .models import Session, Service
from .forms import ServiceForm
>>>>>>> master

class HomeView(TemplateView):
    template_name = 'home.html'


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
                # Get all confirmed sessions for this service
                booked_sessions = Session.objects.filter(
                    service=self.object,
                    status='CONFIRMED'
                ).values_list('date_time', flat=True)

                # Get all confirmed sessions for the coach
                coach_sessions = Session.objects.filter(
                    coach=self.object.coach.profile,
                    status='CONFIRMED'
                ).exclude(service=self.object).values_list('date_time', flat=True)

                # Combine all booked times
                all_booked_times = list(booked_sessions) + list(coach_sessions)
                
                # Get today's date
                today = timezone.now().date()
                
                # Generate available slots for next 7 days
                available_slots = []
                for day in range(7):
                    current_date = today + timezone.timedelta(days=day)
                    for hour in range(9, 18):  # 9 AM to 6 PM
                        slot_time = timezone.make_aware(
                            timezone.datetime.combine(current_date, timezone.time(hour=hour))
                        )
                        
                        # Check if this slot is available
                        is_available = True
                        for booked_time in all_booked_times:
                            if abs((slot_time - booked_time).total_seconds()) < 3600:  # 1 hour
                                is_available = False
                                break
                        
                        if is_available:
                            available_slots.append(slot_time)
                
                context['available_slots'] = available_slots
                context['booked_slots'] = all_booked_times
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

<<<<<<< HEAD

class BookingCreateView(LoginRequiredMixin, CreateView):
    model = Session
    form_class = BookingForm
    template_name = 'viewer/booking_form.html'
    success_url = reverse_lazy('viewer:session_history')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # Pokud je v GET parametr service, předej ho do initial
        service = self.request.GET.get('service')
        if service:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['service'] = service
        return kwargs

    def form_valid(self, form):
        form.instance.client = self.request.user.profile
        service = form.instance.service
        coach_user = service.coach
        try:
            coach_profile = Profile.objects.get(user=coach_user)
            form.instance.coach = coach_profile
            event = create_psychology_session(
                client_email=self.request.user.email,
                start_time=form.instance.date_time,
                duration_minutes=form.instance.service.duration
            )
            messages.success(self.request, f'Session booked successfully! Google Calendar event created: {event.get("htmlLink")}')
        except Profile.DoesNotExist:
            raise Exception(f"Coach {coach_user} nemá profil!")
        except Exception as e:
            print(f"Google Calendar error: {e}")
            messages.warning(self.request, f'Session booked, but failed to create Google Calendar event: {str(e)}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Book a Session'
        context['button_text'] = 'Book Session'
        return context


class SessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Session
    form_class = BookingForm  # nebo vlastní SessionForm, pokud máš
    template_name = 'viewer/booking_form.html'
    success_url = reverse_lazy('viewer:session_history')

    def test_func(self):
        session = self.get_object()
        user = self.request.user

        # Pokud je do začátku session více než 24 hodin, může editovat klient, kouč i admin
        if (session.date_time - timezone.now()).total_seconds() > 24 * 60 * 60:
            return user.profile == session.client or user.profile == session.coach or user.is_superuser

        # Pokud je do začátku méně než 24 hodin, může editovat pouze kouč nebo admin
        return user.profile == session.coach or user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Session'
        context['button_text'] = 'Update Session'
        return context


class SessionCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        session = Session.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        return user.profile == session.client or user.profile == session.coach or user.is_superuser

    def post(self, request, *args, **kwargs):
        session = Session.objects.get(pk=self.kwargs['pk'])
        if session.can_cancel:
            session.status = 'CANCELLED'
            session.save()
            messages.success(request, 'Session has been cancelled successfully.')
        else:
            messages.error(request, 'Cannot cancel session less than 24 hours before start time.')
        return redirect('viewer:session_detail', pk=session.pk)

=======
>>>>>>> master
def home(request):
    return render(request, 'home.html')
