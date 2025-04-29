from django import forms
from django.utils import timezone
from viewer.models import Session, Service, Review

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
        fields = ['name', 'description', 'price', 'duration', 'currency', 'session_type']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['service', 'date_time', 'type', 'notes']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and hasattr(self.user, 'profile'):
            # Filter services based on user type
            if self.user.profile.is_coach:
                self.fields['service'].queryset = Service.objects.filter(
                    coach=self.user,
                    is_active=True
                )
            else:
                self.fields['service'].queryset = Service.objects.filter(
                    is_active=True
                )

    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time:
            if date_time < timezone.now():
                raise forms.ValidationError("Cannot book sessions in the past")
            
            # Check if the time slot is available
            service = self.cleaned_data.get('service')
            if service:
                # Calculate end time based on service duration
                end_time = date_time + timezone.timedelta(minutes=service.duration)
                
                # Check for overlapping sessions
                overlapping = Session.objects.filter(
                    service=service,
                    date_time__lt=end_time,
                    date_time__gt=date_time,
                    status='CONFIRMED'
                ).exists()
                
                if overlapping:
                    raise forms.ValidationError("This time slot is already booked")
        
        return date_time 