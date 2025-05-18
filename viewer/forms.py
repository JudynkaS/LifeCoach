from django import forms
from django.utils import timezone

import datetime
from viewer.models import Session, Service, Review, PaymentMethod

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
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 4}),
            'meeting_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'meeting_address': forms.TextInput(attrs={'placeholder': 'Address for personal session'}),
        }

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
    date_time = forms.ChoiceField(label='Date time*', choices=[], widget=forms.Select())
    duration = forms.IntegerField(label='Duration (minutes)', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    price = forms.DecimalField(label='Price', widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    description = forms.CharField(label='Service Description', widget=forms.Textarea(attrs={'readonly': 'readonly', 'rows': 3}))
    payment_method = forms.ModelChoiceField(queryset=None, label='Payment Method*')
    debug_service = None  # pro debugování
    
    class Meta:
        model = Session
        fields = ['service', 'date_time', 'duration', 'type', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'duration': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        initial_date_time = None
        if 'initial' in kwargs and 'date_time' in kwargs['initial']:
            initial_date_time = kwargs['initial']['date_time']
        super().__init__(*args, **kwargs)
        
        self.fields['service'].widget.attrs.update({
            'onchange': 'updateServiceDetails(this.value)',
            'class': 'form-control'
        })
        
        # DEBUG: Uložím hodnotu service pro výpis do šablony
        service = self.initial.get('service') or self.data.get('service')
        self.debug_service = service
        
        if self.user and hasattr(self.user, 'profile'):
            if self.user.profile.is_coach:
                self.fields['service'].queryset = Service.objects.filter(
                    coach=self.user,
                    is_active=True
                )
                self.fields['date_time'].widget = forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})
            else:
                self.fields['service'].queryset = Service.objects.filter(
                    is_active=True
                )
                if service:
                    try:
                        service_obj = Service.objects.get(pk=int(service))
                        self.initial['duration'] = service_obj.duration
                        self.initial['price'] = service_obj.price
                        self.initial['description'] = service_obj.description
                        self.initial['type'] = service_obj.session_type
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
                    self.fields['date_time'].choices = [("", "Please select a service first")]
                    self.fields['date_time'].widget.attrs['disabled'] = 'disabled'

        from viewer.models import PaymentMethod
        self.fields['payment_method'].queryset = PaymentMethod.objects.all()

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

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        date_time = cleaned_data.get('date_time')
        duration = cleaned_data.get('duration')
        if service and date_time and duration:
            from viewer.models import Session
            # Convert date_time to datetime if it's a string
            if isinstance(date_time, str):
                import datetime
                try:
                    date_time = timezone.make_aware(datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M'))
                except Exception:
                    pass
            start = date_time
            end = date_time + timezone.timedelta(minutes=int(duration))

            # Helper for overlap: (A starts before B ends) and (A ends after B starts)
            def overlaps(qs, who):
                qs = qs.filter(status='CONFIRMED')
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                for s in qs:
                    s_start = s.date_time
                    s_end = s.date_time + timezone.timedelta(minutes=s.duration)
                    if (start < s_end) and (end > s_start):
                        raise forms.ValidationError(
                            f"{who} already has a session that overlaps with this time. (Termín je již obsazený)"
                        )

            # Check for overlapping sessions for the coach
            overlaps(Session.objects.filter(coach=service.coach.profile), "This coach")
            # Check for overlapping sessions for the client
            if self.user and hasattr(self.user, 'profile'):
                overlaps(Session.objects.filter(client=self.user.profile), "You")

        return cleaned_data

