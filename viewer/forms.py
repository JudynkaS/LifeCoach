from django import forms
<<<<<<< HEAD
from django.utils import timezone
from .models import Service, Session, Review
from django.db import models
import datetime
=======
from viewer.models import Session, Service, Review
>>>>>>> master

class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['coach', 'service', 'date_time', 'type', 'notes']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
        }

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'currency', 'session_type', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'duration': forms.NumberInput(attrs={'min': 15, 'step': 15}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
<<<<<<< HEAD
        }

class BookingForm(forms.ModelForm):
    date_time = forms.ChoiceField(label='Date time*', choices=[], widget=forms.Select())
    class Meta:
        model = Session
        fields = ['service', 'date_time', 'duration', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        initial_date_time = None
        if 'initial' in kwargs and 'date_time' in kwargs['initial']:
            initial_date_time = kwargs['initial']['date_time']
        super().__init__(*args, **kwargs)
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.is_coach:
                self.fields['service'].queryset = Service.objects.filter(
                    coach=self.user,
                    is_active=True
                )
                self.fields['date_time'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
            else:
                self.fields['service'].queryset = Service.objects.filter(
                    is_active=True
                )
                service = self.initial.get('service') or self.data.get('service')
                if service:
                    try:
                        service_obj = Service.objects.get(pk=service)
                        today = timezone.now().date()
                        slots = []
                        booked_sessions = Session.objects.filter(
                            service=service_obj,
                            status='CONFIRMED'
                        ).values_list('date_time', flat=True)
                        coach_sessions = Session.objects.filter(
                            coach=service_obj.coach.profile,
                            status='CONFIRMED'
                        ).exclude(service=service_obj).values_list('date_time', flat=True)
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
                                    slots.append((slot_time.strftime('%Y-%m-%d %H:%M'), slot_time.strftime('%A %d.%m.%Y %H:%M')))
                        self.fields['date_time'].choices = slots
                        if initial_date_time:
                            self.initial['date_time'] = initial_date_time
                    except Service.DoesNotExist:
                        self.fields['date_time'].choices = []
                else:
                    self.fields['date_time'].choices = [("", "Nejprve vyberte službu")]
                    self.fields['date_time'].widget.attrs['disabled'] = 'disabled'

    def clean_date_time(self):
        date_time_str = self.cleaned_data.get('date_time')
        from django.utils import timezone
        import datetime
        try:
            date_time = timezone.make_aware(datetime.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M'))
        except Exception:
            raise forms.ValidationError('Invalid date/time format.')
        self.cleaned_data['date_time'] = date_time
        return date_time

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        # Pokud je v GET parametr service, předej ho do initial
        service = self.request.GET.get('service')
        if service:
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['service'] = service
        return kwargs 
=======
        } 
>>>>>>> master
