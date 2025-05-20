from django.shortcuts import redirect, render
from django.views.generic import TemplateView, CreateView, ListView, DetailView, UpdateView, DeleteView, View
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
import os
from django.views.decorators.http import require_GET

from .models import Session, Service, Profile, Review, Payment
from .forms import ServiceForm, BookingForm, ReviewForm, SessionForm, ClientIntakeForm
from .utils.google_calendar import create_coach_calendar_event, delete_coach_calendar_event, update_coach_calendar_event

class HomeView(TemplateView):
    template_name = 'home.html'


class SessionHistoryView(LoginRequiredMixin, ListView):
    model = Session
    template_name = 'viewer/session_history.html'
    context_object_name = 'object_list'
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
        now = timezone.now()
        # Nadcházející sessions (všechny statusy)
        if user_profile.is_coach:
            context['upcoming_sessions'] = Session.objects.filter(
                coach=user_profile,
                date_time__gt=now
            ).order_by('date_time')
            context['past_sessions'] = Session.objects.filter(
                coach=user_profile,
                date_time__lte=now
            ).order_by('-date_time')
        else:
            context['upcoming_sessions'] = Session.objects.filter(
                client=user_profile,
                date_time__gt=now
            ).order_by('date_time')
            context['past_sessions'] = Session.objects.filter(
                client=user_profile,
                date_time__lte=now
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

    def post(self, request, *args, **kwargs):
        session = self.get_object()
        user_profile = request.user.profile
        # Inline potvrzení pouze pro kouče a pouze pokud je session PENDING/CHANGED
        if user_profile.is_coach and session.status in ['PENDING', 'CHANGED']:
            meeting_url = request.POST.get('meeting_url', '').strip()
            meeting_address = request.POST.get('meeting_address', '').strip()
            errors = []
            if session.type == 'online':
                if not meeting_url:
                    errors.append('Online session must have a meeting link.')
                else:
                    session.meeting_url = meeting_url
            elif session.type == 'personal':
                if not meeting_address:
                    errors.append('Personal session must have an address.')
                else:
                    session.meeting_address = meeting_address
            if not errors:
                session.status = 'CONFIRMED'
                session.save()
                messages.success(request, 'Session has been confirmed.')
                return redirect('viewer:session_detail', pk=session.pk)
            else:
                for err in errors:
                    messages.error(request, err)
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_object()
        user_profile = self.request.user.profile
        can_edit_or_cancel = False
        if user_profile == session.client:
            seconds = (session.date_time - timezone.now()).total_seconds()
            if seconds > 24*60*60:
                can_edit_or_cancel = True
        context['can_edit_or_cancel'] = can_edit_or_cancel
        return context


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
        form.instance.status = 'PENDING'
        form.instance.duration = service.duration
        form.instance.type = service.session_type  # Nastaví typ podle servisu
        try:
            coach_profile = Profile.objects.get(user=coach_user)
            form.instance.coach = coach_profile
            # Vytvoření události v Google kalendáři
            event = create_coach_calendar_event(
                coach_profile=coach_profile,
                summary=f"Session with {self.request.user.get_full_name()}",
                description=f"Service: {service.name}\nClient: {self.request.user.get_full_name()}",
                start_dt=form.instance.date_time,
                end_dt=form.instance.date_time + timezone.timedelta(minutes=service.duration),
                timezone_str=str(timezone.get_current_timezone())
            )
            if event:
                form.instance.google_calendar_event_id = event['id']
                messages.success(self.request, f'Session booked successfully! Google Calendar event created: {event.get("htmlLink")}')
                print("DEBUG: Message set - success with calendar")  # Debug print
            else:
                messages.success(self.request, 'Session booked successfully!')
                print("DEBUG: Message set - success without calendar")  # Debug print
        except Profile.DoesNotExist:
            raise Exception(f"Coach {coach_user} nemá profil!")
        except Exception as e:
            print(f"Google Calendar error: {e}")
            messages.warning(self.request, f'Session booked, but failed to create Google Calendar event: {str(e)}')
            print("DEBUG: Message set - warning")  # Debug print
        
        # Uložíme form a vytvoříme session
        response = super().form_valid(form)
        
        # Vytvoření platby
        Payment.objects.create(
            session=self.object,
            amount=service.price,
            payment_method=form.cleaned_data['payment_method']
        )
        
        print("DEBUG: Before redirect")  # Debug print
        # Použijeme redirect z django.shortcuts místo HttpResponseRedirect
        return redirect('viewer:session_history')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.filter(is_active=True)
        context['services'] = services
        # Přidáme JSON se všemi údaji o službách
        context['services_json'] = json.dumps({
            s.pk: {
                'price': str(s.price),
                'duration': s.duration,
                'description': s.description,
            } for s in services
        }, cls=DjangoJSONEncoder)
        context['title'] = 'Book a Session'
        context['button_text'] = 'Book Session'
        return context

class SessionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Session
    form_class = SessionForm
    template_name = 'viewer/booking_form.html'
    success_url = reverse_lazy('viewer:session_history')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # Předvyplníme coach z původní session nebo ze service
        if self.object and not kwargs.get('data'):
            initial = kwargs.get('initial', {})
            initial['coach'] = self.object.coach.id if self.object.coach else self.object.service.coach.profile.id
            kwargs['initial'] = initial
        return kwargs

    def test_func(self):
        session = self.get_object()
        user = self.request.user
        # Kouč nebo admin může potvrdit, klient může editovat/zrušit do 24 hodin před začátkem
        if user.profile.is_coach or user.is_superuser:
            return True
        # Klient může editovat/zrušit pokud je session jeho a do začátku zbývá více než 24 hodin
        return user.profile == session.client and (session.date_time - timezone.now()).total_seconds() > 24 * 60 * 60

    def form_valid(self, form):
        session = form.instance
        original_session = self.get_object()

        # Nastavení coach z původní session nebo ze service
        if not session.coach_id:
            session.coach = original_session.coach if original_session.coach else session.service.coach.profile

        # Nastavení date_time z formuláře nebo původní hodnoty
        if not session.date_time:
            session.date_time = original_session.date_time
        else:
            # Převod na timezone-aware datetime
            try:
                if isinstance(session.date_time, str):
                    naive_dt = datetime.datetime.strptime(session.date_time, '%Y-%m-%dT%H:%M')
                    session.date_time = timezone.make_aware(naive_dt)
            except (ValueError, TypeError):
                form.add_error('date_time', 'Invalid date/time format. Use YYYY-MM-DDTHH:MM format.')
                return self.form_invalid(form)

        # Nastavení type z formuláře, původní session nebo service
        if not session.type:
            session.type = original_session.type or session.service.session_type

        # Validace meeting_url/adresa
        if session.type == 'online' and not session.meeting_url:
            form.add_error('meeting_url', 'Online session must have a meeting link.')
            return self.form_invalid(form)
        if session.type == 'personal' and not session.meeting_address:
            form.add_error('meeting_address', 'Personal session must have an address.')
            return self.form_invalid(form)

        # Potvrzení koučem (status na CONFIRMED) pouze pokud je session PENDING nebo CHANGED
        if self.request.user.profile.is_coach and session.status in ['PENDING', 'CHANGED']:
            if session.coach and session.date_time and session.type:
                if (session.type == 'online' and session.meeting_url) or (session.type == 'personal' and session.meeting_address):
                    session.status = 'CONFIRMED'
                else:
                    if not session.coach:
                        form.add_error('coach', 'This field is required for confirmation.')
                    if not session.date_time:
                        form.add_error('date_time', 'This field is required for confirmation.')
                    if not session.type:
                        form.add_error('type', 'This field is required for confirmation.')
                    return self.form_invalid(form)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['services'] = Service.objects.filter(is_active=True)
        context['title'] = 'Edit Session'
        context['button_text'] = 'Update Session'
        context['session'] = self.object
        context['is_edit'] = True
        return context

class SessionCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        session = Session.objects.get(pk=self.kwargs['pk'])
        user = self.request.user
        # Kouč nebo admin může zrušit jakoukoliv session
        if user.profile.is_coach or user.is_superuser:
            return True
        # Klient může zrušit pouze své session a pouze pokud do začátku zbývá více než 24 hodin
        return user.profile == session.client and (session.date_time - timezone.now()).total_seconds() > 24 * 60 * 60

    def post(self, request, *args, **kwargs):
        session = Session.objects.get(pk=self.kwargs['pk'])
        user = request.user
        
        # Kouč nebo admin může zrušit kdykoliv
        if user.profile.is_coach or user.is_superuser:
            if session.google_calendar_event_id:
                try:
                    delete_coach_calendar_event(session.coach, session.google_calendar_event_id)
                except Exception as e:
                    print(f"Failed to delete Google Calendar event: {e}")
                    messages.warning(request, 'Session cancelled, but failed to delete Google Calendar event.')
            
            session.status = 'CANCELLED'
            session.save()
            messages.success(request, 'Session has been cancelled successfully.')
            return redirect('viewer:session_detail', pk=session.pk)
        
        # Pro klienta kontrolujeme 24 hodin
        if user.profile == session.client:
            if (session.date_time - timezone.now()).total_seconds() > 24 * 60 * 60:
                if session.google_calendar_event_id:
                    try:
                        delete_coach_calendar_event(session.coach, session.google_calendar_event_id)
                    except Exception as e:
                        print(f"Failed to delete Google Calendar event: {e}")
                        messages.warning(request, 'Session cancelled, but failed to delete Google Calendar event.')
                
                session.status = 'CANCELLED'
                session.save()
                messages.success(request, 'Session has been cancelled successfully.')
            else:
                messages.error(request, 'Sessions can only be cancelled more than 24 hours before they start. Please contact your coach for cancellation.')
        
        return redirect('viewer:session_detail', pk=session.pk)

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'viewer/review_form.html'

    def form_valid(self, form):
        session_id = self.kwargs['pk']
        form.instance.session_id = session_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('viewer:session_detail', args=[self.kwargs['pk']])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['session'] = Session.objects.get(pk=self.kwargs['pk'])
        return context

def home(request):
    messages.success(request, 'Toto je testovací zpráva!')
    return render(request, 'home.html')

class CreatePayPalOrderView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        session_id = request.POST.get('session_id')
        if not session_id:
            return HttpResponseBadRequest('Missing session_id')
        try:
            session = Session.objects.get(pk=session_id)
            payment = session.payments.first()
            if not payment:
                return HttpResponseBadRequest('No payment found for this session')
        except Session.DoesNotExist:
            return HttpResponseBadRequest('Session not found')

        # PayPal credentials from .env
        PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
        PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
        PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'  # change to live for production

        # Get access token
        auth_response = requests.post(
            f'{PAYPAL_API_BASE}/v1/oauth2/token',
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={'grant_type': 'client_credentials'},
        )
        if auth_response.status_code != 200:
            return JsonResponse({'error': 'PayPal auth failed'}, status=500)
        access_token = auth_response.json()['access_token']

        # Create order
        order_data = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": payment.payment_method.name.upper() if payment.payment_method.name.upper() in ["USD", "EUR", "CZK"] else "USD",
                        "value": str(payment.amount)
                    },
                    "description": f"Session: {session.service.name} ({session.date_time})"
                }
            ],
            "application_context": {
                "brand_name": "LifeCoach",
                "locale": "en-US",
                "return_url": request.build_absolute_uri(f'/paypal/return/{session.id}/'),
                "cancel_url": request.build_absolute_uri(f'/paypal/cancel/{session.id}/'),
                "user_action": "PAY_NOW"
            }
        }
        order_response = requests.post(
            f'{PAYPAL_API_BASE}/v2/checkout/orders',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            },
            json=order_data
        )
        if order_response.status_code != 201:
            return JsonResponse({'error': 'Failed to create PayPal order', 'details': order_response.json()}, status=500)
        order = order_response.json()
        approval_url = next((l['href'] for l in order['links'] if l['rel'] == 'approve'), None)
        if not approval_url:
            return JsonResponse({'error': 'Failed to get PayPal approval URL'}, status=500)
        # Optionally save order_id to payment
        payment.transaction_id = order['id']
        payment.save()
        return JsonResponse({'approval_url': approval_url})

class PayPalReturnView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        from django.contrib import messages
        session = Session.objects.get(pk=session_id)
        payment = session.payments.first()
        order_id = payment.transaction_id
        # PayPal credentials
        PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID')
        PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET')
        PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'
        # Get access token
        auth_response = requests.post(
            f'{PAYPAL_API_BASE}/v1/oauth2/token',
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={'grant_type': 'client_credentials'},
        )
        access_token = auth_response.json()['access_token']
        # Get order details
        order_response = requests.get(
            f'{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {access_token}'
            }
        )
        order = order_response.json()
        if order.get('status') == 'COMPLETED' or order.get('status') == 'APPROVED':
            payment.paid_at = timezone.now()
            payment.save()
            messages.success(request, 'Payment completed successfully!')
        else:
            messages.warning(request, 'Payment not completed. Please try again.')
        return redirect('viewer:session_detail', pk=session_id)

class PayPalCancelView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        from django.contrib import messages
        messages.warning(request, 'Payment was cancelled.')
        return redirect('viewer:session_detail', pk=session_id)

@require_GET
@csrf_exempt
def service_details_api(request):
    from .models import Service, Session
    import datetime
    from django.utils import timezone
    service_id = request.GET.get('service')
    if not service_id:
        return JsonResponse({'error': 'Missing service id'}, status=400)
    try:
        service = Service.objects.get(pk=service_id)
    except Service.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)
    # Detaily služby
    data = {
        'price': str(service.price),
        'duration': service.duration,
        'description': service.description,
        'type': service.session_type,
    }
    # Sloty
    today = timezone.now().date()
    slots = []
    booked_sessions = Session.objects.filter(
        service=service,
        status='CONFIRMED'
    ).values_list('date_time', flat=True)
    coach_sessions = Session.objects.filter(
        coach=service.coach.profile,
        status='CONFIRMED'
    ).exclude(service=service).values_list('date_time', flat=True)
    all_booked_times = list(booked_sessions) + list(coach_sessions)
    for day in range(7):
        current_date = today + timezone.timedelta(days=day)
        for hour in range(9, 18):
            slot_time = timezone.make_aware(
                datetime.datetime.combine(current_date, datetime.time(hour=hour))
            )
            is_available = True
            for booked_time in all_booked_times:
                if abs((slot_time - booked_time).total_seconds()) < 3600:
                    is_available = False
                    break
            if is_available:
                slots.append({
                    'value': slot_time.strftime('%Y-%m-%d %H:%M'),
                    'label': slot_time.strftime('%A %d.%m.%Y %H:%M')
                })
    data['slots'] = slots
    return JsonResponse(data)

def client_intake(request):
    if not request.user.is_authenticated or request.user.profile.is_coach:
        return redirect('viewer:home')
    
    if request.method == 'POST':
        form = ClientIntakeForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your intake form has been submitted successfully.')
            return redirect('accounts:profile', pk=request.user.profile.pk)
    else:
        form = ClientIntakeForm(instance=request.user.profile)
    
    return render(request, 'viewer/client_intake.html', {'form': form})
