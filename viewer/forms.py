from django import forms
from django.utils import timezone
import pytz

import datetime
from viewer.models import Session, Service, Review, PaymentMethod
from django.db import transaction
from accounts.models import Profile

class BaseStyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing_class = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_class + ' form-control').strip()

class SessionForm(BaseStyledForm):
    class Meta:
        model = Session
        fields = ['coach', 'service', 'date_time', 'type', 'notes', 'meeting_url', 'meeting_address']
        widgets = {
            'date_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                    'required': True
                }
            ),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'meeting_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'meeting_address': forms.TextInput(attrs={'placeholder': 'Address for personal session'}),
            'coach': forms.HiddenInput(),
            'service': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Pokud máme instanci (existující session)
        if self.instance and self.instance.pk:
            # Nastavíme coach z instance nebo ze service
            if self.instance.coach:
                self.initial['coach'] = self.instance.coach.id
            elif self.instance.service and self.instance.service.coach:
                self.initial['coach'] = self.instance.service.coach.profile.id
                self.instance.coach = self.instance.service.coach.profile
            
            # Service by neměl být editovatelný při potvrzení
            if self.instance.service:
                self.initial['service'] = self.instance.service.id
                self.fields['service'].widget = forms.HiddenInput()
            
            # Nastavení date_time do správného formátu pro datetime-local input
            if self.instance.date_time:
                if self.user and hasattr(self.user, 'profile') and self.user.profile.timezone:
                    user_tz = pytz.timezone(self.user.profile.timezone)
                    local_dt = self.instance.date_time.astimezone(user_tz)
                else:
                    local_dt = self.instance.date_time.astimezone()
                self.initial['date_time'] = local_dt.strftime('%Y-%m-%dT%H:%M')
                self.fields['date_time'].initial = local_dt.strftime('%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        
        # Pokud není coach ve formuláři, nastavíme ho z instance nebo service
        if not cleaned_data.get('coach'):
            if self.instance and self.instance.service and self.instance.service.coach:
                cleaned_data['coach'] = self.instance.service.coach.profile
            elif self.instance and self.instance.coach:
                cleaned_data['coach'] = self.instance.coach
            elif hasattr(self, 'user') and hasattr(self.user, 'profile') and self.user.profile.is_coach:
                cleaned_data['coach'] = self.user.profile
        
        # Pokud není date_time ve formuláři, použijeme hodnotu z instance
        if not cleaned_data.get('date_time') and self.instance and self.instance.date_time:
            cleaned_data['date_time'] = self.instance.date_time
        
        return cleaned_data

class ServiceForm(BaseStyledForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price', 'duration', 'currency', 'session_type', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'duration': forms.NumberInput(attrs={'min': 15, 'step': 15}),
        }

class ReviewForm(BaseStyledForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class BookingForm(BaseStyledForm):
    date_time = forms.ChoiceField(
        label='Date time*',
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    duration = forms.IntegerField(
        label='Duration (minutes)',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'class': 'form-control',
            'style': 'background-color: #f8f9fa; border: 1px solid #dee2e6;'
        })
    )
    price = forms.DecimalField(
        label='Price',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'class': 'form-control',
            'style': 'background-color: #f8f9fa; border: 1px solid #dee2e6;'
        })
    )
    description = forms.CharField(
        label='Service Description',
        required=False,
        widget=forms.Textarea(attrs={
            'readonly': True,
            'class': 'form-control',
            'rows': 3,
            'style': 'background-color: #f8f9fa; border: 1px solid #dee2e6;'
        })
    )
    type = forms.CharField(
        label='Type',
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': True,
            'class': 'form-control',
            'style': 'background-color: #f8f9fa; border: 1px solid #dee2e6;'
        })
    )
    payment_method = forms.ModelChoiceField(
        queryset=None,
        label='Payment Method*',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Session
        fields = ['service', 'date_time', 'notes']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_service_select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any notes or special requests here...'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        initial_date_time = None
        if 'initial' in kwargs and 'date_time' in kwargs['initial']:
            initial_date_time = kwargs['initial']['date_time']
        super().__init__(*args, **kwargs)

        # Nastavení service queryset podle role uživatele
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.is_coach:
                self.fields['service'].queryset = Service.objects.filter(
                    coach=self.user,
                    is_active=True
                )
            else:
                self.fields['service'].queryset = Service.objects.filter(
                    is_active=True
                )

        # Načtení service a předvyplnění hodnot
        service = self.initial.get('service') or self.data.get('service')
        if service:
            try:
                service_obj = Service.objects.get(pk=int(service))
                # Nastavení hodnot ze service jako readonly
                self.initial['duration'] = service_obj.duration
                self.initial['price'] = service_obj.price
                self.initial['description'] = service_obj.description
                self.initial['type'] = service_obj.session_type

                # Generování dostupných časových slotů
                today = timezone.now().date()
                slots = []
                booked_sessions = Session.objects.filter(
                    service=service_obj,
                    status__in=['CONFIRMED', 'PENDING']
                ).values_list('date_time', flat=True)
                coach_sessions = Session.objects.filter(
                    coach=service_obj.coach.profile,
                    status__in=['CONFIRMED', 'PENDING']
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
                            slots.append((
                                slot_time.strftime('%Y-%m-%d %H:%M'),
                                slot_time.strftime('%A %d.%m.%Y %H:%M')
                            ))
                self.fields['date_time'].choices = slots
                if initial_date_time:
                    self.initial['date_time'] = initial_date_time
            except Service.DoesNotExist:
                self.fields['date_time'].choices = []
        else:
            self.fields['date_time'].choices = [("", "Please select a service first")]
            self.fields['date_time'].widget.attrs['disabled'] = 'disabled'

        # Nastav queryset pro payment_method
        self.fields['payment_method'].queryset = PaymentMethod.objects.all()

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        if service:
            # Ověření, že hodnoty odpovídají service
            cleaned_data['duration'] = service.duration
            cleaned_data['price'] = service.price
            cleaned_data['type'] = service.session_type
        return cleaned_data

class ClientIntakeForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'medical_conditions',
            'emotional_treatment_history',
            'goals',
            'fears_phobias',
            'therapy_consent'
        ]
        widgets = {
            'medical_conditions': forms.Textarea(attrs={'rows': 3}),
            'emotional_treatment_history': forms.Textarea(attrs={'rows': 3}),
            'goals': forms.Textarea(attrs={'rows': 3}),
            'fears_phobias': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

