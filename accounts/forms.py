from django.contrib.auth.forms import UserCreationForm
from django.db.transaction import atomic
from django.forms import CharField, PasswordInput, DateField, NumberInput, \
    Textarea, ModelForm, TextInput, Select, CheckboxSelectMultiple
from django import forms
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div, Submit
from crispy_forms.bootstrap import FormActions
import re
import logging

from accounts.models import (
    Profile, PHONE_PREFIXES, SPECIALIZATION_CHOICES, GOALS_CHOICES,
    MARITAL_STATUS_CHOICES, MEDICAL_CONDITIONS, REFERRAL_SOURCES, TIMEZONE_CHOICES, CONTACT_CHOICES
)

class SignUpForm(UserCreationForm):
    is_coach = forms.BooleanField(
        required=False,
        label='Register as a Coach',
        help_text='Check this if you want to register as a coach'
    )

    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2', 'middle_initial', 'date_of_birth', 'sex', 'marital_status', 'occupation',
                  'street_address', 'city', 'state', 'zip_code', 'phone_prefix', 'phone', 'timezone', 'preferred_contact',
                  'emotional_treatment', 'emotional_treatment_explanation', 'medical_conditions', 'specialization', 'goals', 'fears_phobias', 'referral_source', 'referral_source_other', 'therapy_consent']

        labels = {
            'username': 'Username *',
            'first_name': 'First Name *',
            'last_name': 'Last Name *',
            'email': 'Email *',
        }

        help_texts = {
            'username': 'Allowed characters: letters, numbers and @/./+/-/_',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-6'),
                Column('email', css_class='form-group col-md-6'),
            ),
            Row(
                Column('first_name', css_class='form-group col-md-6'),
                Column('last_name', css_class='form-group col-md-6'),
            ),
            Row(
                Column('password1', css_class='form-group col-md-6'),
                Column('password2', css_class='form-group col-md-6'),
            ),
            HTML('<hr class="my-4">'),
            HTML('<h4 class="mb-3">Personal Information</h4>'),
            Row(
                Column('middle_initial', css_class='form-group col-md-2'),
                Column('date_of_birth', css_class='form-group col-md-5'),
                Column('sex', css_class='form-group col-md-5'),
            ),
            Row(
                Column('marital_status', css_class='form-group col-md-6'),
                Column('occupation', css_class='form-group col-md-6'),
            ),
            HTML('<hr class="my-4">'),
            HTML('<h4 class="mb-3">Contact Information</h4>'),
            Row(
                Column('street_address', css_class='form-group col-12'),
            ),
            Row(
                Column('city', css_class='form-group col-md-4'),
                Column('state', css_class='form-group col-md-4'),
                Column('zip_code', css_class='form-group col-md-4'),
            ),
            Row(
                Column('phone_prefix', css_class='form-group col-md-3'),
                Column('phone', css_class='form-group col-md-9'),
            ),
            Row(
                Column('timezone', css_class='form-group col-md-6'),
                Column('preferred_contact', css_class='form-group col-md-6'),
            ),
            HTML('<hr class="my-4">'),
            HTML('<h4 class="mb-3">Role Selection</h4>'),
            'is_coach',
            HTML('<div id="coach-fields" style="display: none;">'),
            HTML('<h4 class="mb-3">Coach Information</h4>'),
            'specialization',
            'bio',
            HTML('</div>'),
            HTML('<div id="client-fields">'),
            HTML('<h4 class="mb-3">Client Information</h4>'),
            'goals',
            'fears_phobias',
            'emotional_treatment',
            'emotional_treatment_explanation',
            'medical_conditions',
            'referral_source',
            'referral_source_other',
            'therapy_consent',
            HTML('</div>'),
        )

    username = CharField(
        max_length=30,
        required=True,
        label='Username *',
        validators=[
            RegexValidator(
                r'^[\w.@+-]+$',
                'This value may contain only letters, numbers and @/./+/-/_ characters.'
            ),
        ]
    )

    password1 = CharField(
        widget=PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control password-input',
            'data-toggle': 'password'
        }),
        label='Password *'
    )

    password2 = CharField(
        widget=PasswordInput(attrs={
            'placeholder': 'Password again',
            'class': 'form-control password-input',
            'data-toggle': 'password'
        }),
        label='Password Again *'
    )

    # Personal Information
    middle_initial = CharField(
        max_length=1,
        required=False,
        label='Middle Initial',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    street_address = CharField(
        max_length=255,
        required=True,
        label='Street Address *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    city = CharField(
        max_length=100,
        required=True,
        label='City *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    state = CharField(
        max_length=100,
        required=True,
        label='State *',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    zip_code = CharField(
        max_length=10,
        required=True,
        label='ZIP Code *',
        validators=[
            RegexValidator(
                r'^\d{3}\s?\d{2}$',
                'Enter ZIP code in format XXX XX or XXXXX'
            ),
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX XX'
        })
    )

    # Contact Information
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIXES,
        initial='+1',
        label='Country Code',
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    phone = CharField(
        label='Mobile Phone',
        required=False,
        validators=[
            RegexValidator(
                r'^\d{9}$',
                'Enter 9 digits of phone number without spaces or prefix'
            ),
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456789'
        })
    )

    # Additional Personal Information
    date_of_birth = forms.DateField(
        required=True,
        label='Birth Date *',
        input_formats=['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'DD.MM.RRRR'
        }),
        help_text='Formát: DD.MM.RRRR nebo DD/MM/RRRR'
    )

    sex = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        required=True,
        label='Sex *',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    marital_status = forms.ChoiceField(
        choices=MARITAL_STATUS_CHOICES,
        required=False,
        label='Marital Status',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    occupation = CharField(
        max_length=100,
        required=False,
        label='Occupation',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Medical History
    emotional_treatment = forms.BooleanField(
        required=False,
        label='Have you ever been treated for an emotional problem?',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    emotional_treatment_explanation = forms.CharField(
        required=False,
        label='If yes, please explain:',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Describe your experience...'
        })
    )

    medical_conditions = forms.MultipleChoiceField(
        choices=MEDICAL_CONDITIONS,
        required=False,
        label='Have you ever been treated for:',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'medical-conditions-group list-unstyled'
        })
    )

    # Goals and Interests
    specialization = forms.MultipleChoiceField(
        choices=SPECIALIZATION_CHOICES,
        required=False,
        label='Area of Focus',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'goals-checkbox-group list-unstyled'})
    )

    goals = forms.MultipleChoiceField(
        choices=GOALS_CHOICES,
        required=False,
        label='Goals',
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'goals-checkbox-group list-unstyled'
        })
    )

    fears_phobias = forms.CharField(
        required=False,
        label='Do you have any fears or phobias?',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Describe your fears or phobias...'
        })
    )

    # Referral Information
    referral_source = forms.MultipleChoiceField(
        choices=REFERRAL_SOURCES,
        required=False,
        label='How did you hear about us?',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'referral-checkbox-group'})
    )

    referral_source_other = forms.CharField(
        required=False,
        label='Other referral source:',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Consent
    therapy_consent = forms.BooleanField(
        required=True,
        label='I understand and agree to the terms *',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    hypnotherapy_consent = forms.BooleanField(
        required=True,
        label='',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        required=True,
        label='Time Zone',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    preferred_contact = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        required=True,
        label='Preferred Contact Method',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        if zip_code:
            # Remove spaces and check format
            zip_code = ''.join(zip_code.split())
            if not re.match(r'^\d{5}$', zip_code):
                raise forms.ValidationError('Enter ZIP code in format XXX XX or XXXXX')
            # Format as XXX XX
            return f'{zip_code[:3]} {zip_code[3:]}'
        return zip_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and other characters
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) != 9:
                raise forms.ValidationError('Phone number must have 9 digits')
        return phone

    @atomic
    def save(self, commit=True):
        try:
            user = super().save(commit=False)
            user.is_active = True
            if commit:
                user.save()

            # Create profile with all the form data
            profile = Profile(
                user=user,
                middle_initial=self.cleaned_data.get('middle_initial'),
                street_address=self.cleaned_data.get('street_address'),
                city=self.cleaned_data.get('city'),
                state=self.cleaned_data.get('state'),
                zip_code=self.cleaned_data.get('zip_code'),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                sex=self.cleaned_data.get('sex'),
                marital_status=self.cleaned_data.get('marital_status'),
                occupation=self.cleaned_data.get('occupation'),
                
                # Contact Information
                phone=f"{self.cleaned_data.get('phone_prefix')}{self.cleaned_data.get('phone')}",
                timezone=self.cleaned_data.get('timezone'),
                preferred_contact=self.cleaned_data.get('preferred_contact'),
                
                # Medical History
                emotional_treatment_history=self.cleaned_data.get('emotional_treatment_explanation') if self.cleaned_data.get('emotional_treatment') else None,
                medical_conditions=self.cleaned_data.get('medical_conditions', []),
                
                # Goals and Interests
                specialization=self.cleaned_data.get('specialization'),
                goals=self.cleaned_data.get('goals'),
                fears_phobias=self.cleaned_data.get('fears_phobias'),
                
                # Role
                is_coach=self.cleaned_data.get('is_coach', False),
                is_client=not self.cleaned_data.get('is_coach', False),
            )
            
            if commit:
                profile.save()
            
            return user
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error saving user/profile: {str(e)}")
            raise


class ProfileUpdateForm(ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='First Name')
    last_name = forms.CharField(max_length=30, required=True, label='Last Name')
    date_of_birth = forms.DateField(
        required=True,
        label='Birth Date',
        input_formats=['%d.%m.%Y', '%d/%m/%Y', '%Y-%m-%d'],
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'text',
            'placeholder': 'DD.MM.RRRR'
        })
    )
    sex = forms.ChoiceField(
        choices=[('M', 'Male'), ('F', 'Female')],
        required=True,
        label='Sex',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    street_address = forms.CharField(
        max_length=255,
        required=True,
        label='Street Address',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        label='City',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    state = forms.CharField(
        max_length=100,
        required=True,
        label='State',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    zip_code = forms.CharField(
        max_length=10,
        required=True,
        label='ZIP Code',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXX XX'})
    )
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIXES,
        initial='+1',
        label='Country Code',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    phone = forms.CharField(
        label='Mobile Phone',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '123456789'
        })
    )
    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,
        required=True,
        label='Time Zone',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    preferred_contact = forms.ChoiceField(
        choices=CONTACT_CHOICES,
        required=True,
        label='Preferred Contact Method',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    specialization = forms.CharField(
        required=False,
        label='Specialization',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your specialization, focus, etc.'})
    )
    goals = forms.MultipleChoiceField(
        choices=GOALS_CHOICES,
        required=False,
        label='Goals',
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'goals-checkbox-group'})
    )
    marital_status = forms.ChoiceField(
        choices=MARITAL_STATUS_CHOICES,
        required=False,
        label='Marital Status',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    occupation = forms.CharField(
        max_length=100,
        required=False,
        label='Occupation',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    notifications_enabled = forms.BooleanField(
        required=False,
        label='Enable Notifications',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    avatar = forms.ImageField(
        required=False,
        label='Profile Picture',
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    bio = forms.CharField(
        required=False,
        label='Biography',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

    class Meta:
        model = Profile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'sex', 'marital_status', 'occupation',
            'street_address', 'city', 'state', 'zip_code',
            'phone_prefix', 'phone', 'timezone', 'specialization', 'goals', 'bio',
            'preferred_contact', 'notifications_enabled', 'avatar'
        ]
        labels = {
            'phone': 'Phone Number',
            'timezone': 'Time Zone',
            'preferred_contact': 'Preferred Contact Method',
            'notifications_enabled': 'Enable Notifications',
            'avatar': 'Profile Picture',
            'bio': 'Biography'
        }
        widgets = {
            'bio': Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'phone': TextInput(attrs={'placeholder': '123456789', 'class': 'form-control'}),
            'timezone': Select(attrs={'class': 'form-select'}),
            'preferred_contact': Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.phone:
            # Split phone number into prefix and number
            for prefix, _ in PHONE_PREFIXES:
                if self.instance.phone.startswith(prefix):
                    self.initial['phone_prefix'] = prefix
                    self.initial['phone'] = self.instance.phone[len(prefix):]
                    break
        # Set initial goals from comma-separated string
        if self.instance and self.instance.goals:
            self.initial['goals'] = self.instance.get_goals_list()
        # Set initial values for first name and last name from user model
        if self.instance and self.instance.user:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
        # Set initial values for new fields
        if self.instance:
            self.initial['date_of_birth'] = self.instance.date_of_birth
            self.initial['sex'] = self.instance.sex
            self.initial['marital_status'] = self.instance.marital_status
            self.initial['occupation'] = self.instance.occupation
            self.initial['street_address'] = self.instance.street_address
            self.initial['city'] = self.instance.city
            self.initial['state'] = self.instance.state
            self.initial['zip_code'] = self.instance.zip_code

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            # Remove spaces and dashes
            phone = ''.join(filter(str.isdigit, phone))
            if len(phone) < 9:
                raise forms.ValidationError('Phone number must have at least 9 digits.')
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        prefix = cleaned_data.get('phone_prefix')
        goals = cleaned_data.get('goals', [])
        if phone and prefix:
            # Combine prefix and number
            cleaned_data['phone'] = f"{prefix}{phone}"
        # Convert goals list to comma-separated string
        if goals:
            cleaned_data['goals'] = ','.join(goals)
        # Generate bio if specialization or goals changed
        if 'specialization' in self.changed_data or 'goals' in self.changed_data:
            self.instance.specialization = cleaned_data.get('specialization')
            self.instance.goals = cleaned_data.get('goals')
            cleaned_data['bio'] = self.instance.generate_bio()
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Save first name and last name to user model
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            profile.save()
        return profile
