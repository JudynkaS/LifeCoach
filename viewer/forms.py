from django import forms
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
        } 