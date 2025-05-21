from django.contrib.auth.forms import UserCreationForm
from django.db.transaction import atomic
from django.forms import (
    CharField,
    PasswordInput,
    DateField,
    NumberInput,
    Textarea,
    ModelForm,
    TextInput,
    Select,
    CheckboxSelectMultiple,
)
from django import forms
from django.core.validators import RegexValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field, HTML, Div, Submit
from crispy_forms.bootstrap import FormActions
import re

from accounts.models import (
    Profile,
    PHONE_PREFIXES,
    SPECIALIZATION_CHOICES,
    GOALS_CHOICES,
    MARITAL_STATUS_CHOICES,
    MEDICAL_CONDITIONS,
    REFERRAL_SOURCES,
    TIMEZONE_CHOICES,
    CONTACT_CHOICES,
)


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        ]

        labels = {
            "username": "Username *",
            "first_name": "First Name *",
            "last_name": "Last Name *",
            "email": "Email *",
        }

        help_texts = {
            "username": "Allowed characters: letters, numbers and @/./+/-/_",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form-horizontal"
        self.helper.label_class = "col-lg-3"
        self.helper.field_class = "col-lg-9"
        self.helper.layout = Layout(
            # Account Information
            HTML("<h4 class='mb-3'>Account Information</h4>"),
            Row(
                Column("username", css_class="col-md-6"),
                Column("email", css_class="col-md-6"),
                css_class="g-3",
            ),
            Row(
                Column("password1", css_class="col-md-6"),
                Column("password2", css_class="col-md-6"),
                css_class="g-3 mt-3",
            ),
            HTML("<hr>"),
            # Personal Information
            HTML("<h4 class='mb-3'>Personal Information</h4>"),
            Row(
                Column("first_name", css_class="col-md-4"),
                Column("middle_initial", css_class="col-md-2"),
                Column("last_name", css_class="col-md-6"),
                css_class="g-3",
            ),
            Row(
                Column("date_of_birth", css_class="col-md-4"),
                Column("sex", css_class="col-md-4"),
                Column("marital_status", css_class="col-md-4"),
                css_class="g-3 mt-3",
            ),
            Row(Column("occupation", css_class="col-12"), css_class="mt-3"),
            HTML("<hr>"),
            # Address
            HTML("<h4 class='mb-3'>Address</h4>"),
            Row(Column("street_address", css_class="col-12"), css_class="mb-3"),
            Row(
                Column("city", css_class="col-md-5"),
                Column("state", css_class="col-md-4"),
                Column("zip_code", css_class="col-md-3"),
                css_class="g-3",
            ),
            HTML("<hr>"),
            # Contact
            HTML("<h4 class='mb-3'>Contact</h4>"),
            Row(
                Column("phone_prefix", css_class="col-md-4"),
                Column("phone", css_class="col-md-8"),
                css_class="g-3",
            ),
            HTML("<hr>"),
            # Medical History
            HTML("<h4 class='mb-3'>Medical History</h4>"),
            Row(
                Column(Field("emotional_treatment"), css_class="col-12"),
                css_class="mb-2",
            ),
            Row(
                Column("emotional_treatment_explanation", css_class="col-12"),
                css_class="mb-2",
                css_id="emotional-explanation",
                style="display: none;",
            ),
            Row(
                Column(Field("medical_conditions"), css_class="col-12"),
                css_class="mb-4",
            ),
            HTML("<hr>"),
            # Goals and Interests
            HTML("<h4 class='mb-3'>Goals and Interests</h4>"),
            Row(Column("specialization", css_class="col-12"), css_class="mb-3"),
            HTML("<hr>"),
            # Consent
            # Consent – text bude v HTML, checkbox se zobrazí až v šabloně ručně
            HTML("<h4 class='mb-3'>Consent</h4>"),
        )

        # Add submit button
        self.helper.add_input(
            Submit(
                "submit",
                "Create Account",
                css_class="btn btn-success btn-lg w-100 mt-4",
            )
        )

    username = CharField(
        max_length=30,
        required=True,
        label="Username *",
        validators=[
            RegexValidator(
                r"^[\w.@+-]+$",
                "This value may contain only letters, numbers and @/./+/-/_ characters.",
            ),
        ],
    )

    password1 = CharField(
        widget=PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control password-input",
                "data-toggle": "password",
            }
        ),
        label="Password *",
    )

    password2 = CharField(
        widget=PasswordInput(
            attrs={
                "placeholder": "Password again",
                "class": "form-control password-input",
                "data-toggle": "password",
            }
        ),
        label="Password Again *",
    )

    # Personal Information
    middle_initial = CharField(
        max_length=1,
        required=False,
        label="Middle Initial",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    street_address = CharField(
        max_length=255,
        required=True,
        label="Street Address *",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    city = CharField(
        max_length=100,
        required=True,
        label="City *",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    state = CharField(
        max_length=100,
        required=True,
        label="State *",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    zip_code = CharField(
        max_length=10,
        required=True,
        label="ZIP Code *",
        validators=[
            RegexValidator(
                r"^\d{3}\s?\d{2}$", "Enter ZIP code in format XXX XX or XXXXX"
            ),
        ],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "XXX XX"}
        ),
    )

    # Contact Information
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIXES,
        initial="+1",
        label="Country Code",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    phone = CharField(
        label="Mobile Phone",
        required=False,
        validators=[
            RegexValidator(
                r"^\d{9}$", "Enter 9 digits of phone number without spaces or prefix"
            ),
        ],
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "123456789"}
        ),
    )

    # Additional Personal Information
    date_of_birth = forms.DateField(
        required=True,
        label="Birth Date *",
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        help_text="Format: MM/DD/YYYY",
    )

    sex = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female")],
        required=True,
        label="Sex *",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    marital_status = forms.ChoiceField(
        choices=MARITAL_STATUS_CHOICES,
        required=False,
        label="Marital Status",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    occupation = CharField(
        max_length=100,
        required=False,
        label="Occupation",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Medical History
    emotional_treatment = forms.BooleanField(
        required=False,
        label="Have you ever been treated for an emotional problem?",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    emotional_treatment_explanation = forms.CharField(
        required=False,
        label="If yes, please explain:",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Describe your experience...",
            }
        ),
    )

    medical_conditions = forms.MultipleChoiceField(
        choices=MEDICAL_CONDITIONS,
        required=False,
        label="Have you ever been treated for:",
        widget=forms.CheckboxSelectMultiple(
            attrs={"class": "medical-conditions-group list-unstyled"}
        ),
    )

    # Goals and Interests
    specialization = forms.ChoiceField(
        choices=[("", "-- Select Area of Focus --")] + list(SPECIALIZATION_CHOICES),
        required=False,
        label="Area of Focus",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    fears_phobias = forms.CharField(
        required=False,
        label="Do you have any fears or phobias?",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Describe your fears or phobias...",
            }
        ),
    )

    # Referral Information
    referral_source = forms.ChoiceField(
        choices=REFERRAL_SOURCES, required=False, label="How did you hear about us?"
    )

    referral_source_other = forms.CharField(
        required=False,
        label="Other referral source:",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # Consent
    therapy_consent = forms.BooleanField(
        required=True,
        label="I understand and agree to the terms *",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean_zip_code(self):
        zip_code = self.cleaned_data.get("zip_code")
        if zip_code:
            # Remove spaces and check format
            zip_code = "".join(zip_code.split())
            if not re.match(r"^\d{5}$", zip_code):
                raise forms.ValidationError("Enter ZIP code in format XXX XX or XXXXX")
            # Format as XXX XX
            return f"{zip_code[:3]} {zip_code[3:]}"
        return zip_code

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Remove spaces and other characters
            phone = "".join(filter(str.isdigit, phone))
            if len(phone) != 9:
                raise forms.ValidationError("Phone number must have 9 digits")
        return phone

    @atomic
    def save(self, commit=True):
        self.instance.is_active = True
        user = super().save(commit)
        # Nastav jméno a příjmení do User modelu
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.save()

        # Kontrola, zda už profil existuje
        if Profile.objects.filter(user=user).exists():
            return user

        # Create profile with all the form data
        profile = Profile(
            user=user,
            middle_initial=self.cleaned_data.get("middle_initial"),
            street_address=self.cleaned_data.get("street_address"),
            city=self.cleaned_data.get("city"),
            state=self.cleaned_data.get("state"),
            zip_code=self.cleaned_data.get("zip_code"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            sex=self.cleaned_data.get("sex"),
            marital_status=self.cleaned_data.get("marital_status"),
            occupation=self.cleaned_data.get("occupation"),
            # Contact Information
            phone=f"{self.cleaned_data.get('phone_prefix')}{self.cleaned_data.get('phone')}",
            # Medical History
            emotional_treatment_history=(
                self.cleaned_data.get("emotional_treatment_explanation")
                if self.cleaned_data.get("emotional_treatment")
                else None
            ),
            medical_conditions=self.cleaned_data.get("medical_conditions", []),
            # Goals and Interests
            specialization=self.cleaned_data.get("specialization"),
            fears_phobias=self.cleaned_data.get("fears_phobias"),
            # Referral Information
            referral_source=self.cleaned_data.get("referral_source"),
            referral_source_other=self.cleaned_data.get("referral_source_other"),
            # Consent
            therapy_consent=self.cleaned_data.get("therapy_consent", False),
            # Set default values
            is_coach=False,
            is_client=True,
        )

        # Generate bio if specialization is set
        if profile.specialization:
            profile.bio = profile.generate_bio()

        if commit:
            profile.save()
        return user


class ProfileUpdateForm(ModelForm):
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIXES, initial="+1", label="Country Code"
    )

    specialization = forms.CharField(
        required=False,
        label="Specialization",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "* Self-discovery & personal growth\n* Confidence building\n* Life transitions (career, relationships, identity)",
            }
        ),
    )

    # Přidávám pole pro jméno a příjmení
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")

    class Meta:
        model = Profile
        fields = [
            "first_name",
            "last_name",
            "phone_prefix",
            "phone",
            "timezone",
            "specialization",
            "bio",
            "preferred_contact",
            "notifications_enabled",
            "avatar",
        ]
        labels = {
            "phone": "Phone Number",
            "timezone": "Time Zone",
            "preferred_contact": "Preferred Contact Method",
            "notifications_enabled": "Enable Notifications",
            "avatar": "Profile Picture",
            "bio": "Biography",
            "specialization": "Specialization",
        }
        widgets = {
            "bio": Textarea(attrs={"rows": 4, "class": "form-control"}),
            "phone": TextInput(
                attrs={"placeholder": "123456789", "class": "form-control"}
            ),
            "timezone": Select(attrs={"class": "form-select"}),
            "preferred_contact": Select(attrs={"class": "form-select"}),
            "specialization": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Psychotherapy, Mindfulness, ...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.phone:
            # Split phone number into prefix and number
            for prefix, _ in PHONE_PREFIXES:
                if self.instance.phone.startswith(prefix):
                    self.initial["phone_prefix"] = prefix
                    self.initial["phone"] = self.instance.phone[len(prefix) :]
                    break
        # Nastavím počáteční hodnoty pro jméno a příjmení z user modelu
        if self.instance and self.instance.user:
            self.initial["first_name"] = self.instance.user.first_name
            self.initial["last_name"] = self.instance.user.last_name

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            # Remove spaces and dashes
            phone = "".join(filter(str.isdigit, phone))
            if len(phone) < 9:
                raise forms.ValidationError("Phone number must have at least 9 digits.")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        prefix = cleaned_data.get("phone_prefix")
        if phone and prefix:
            # Combine prefix and number
            cleaned_data["phone"] = f"{prefix}{phone}"
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Uložím jméno a příjmení do user modelu
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile.save()
        return profile


class ClientProfileUpdateForm(ModelForm):
    phone_prefix = forms.ChoiceField(
        choices=PHONE_PREFIXES, initial="+1", label="Country Code"
    )
    first_name = forms.CharField(max_length=30, required=True, label="First Name")
    last_name = forms.CharField(max_length=30, required=True, label="Last Name")
    middle_initial = forms.CharField(
        max_length=1, required=False, label="Middle Initial"
    )
    street_address = forms.CharField(
        max_length=255, required=True, label="Street Address"
    )
    city = forms.CharField(max_length=100, required=True, label="City")
    state = forms.CharField(max_length=100, required=True, label="State")
    zip_code = forms.CharField(max_length=10, required=True, label="ZIP Code")
    date_of_birth = forms.DateField(
        required=True,
        label="Birth Date",
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    sex = forms.ChoiceField(
        choices=[("M", "Male"), ("F", "Female")], required=True, label="Sex"
    )
    marital_status = forms.ChoiceField(
        choices=MARITAL_STATUS_CHOICES, required=False, label="Marital Status"
    )
    occupation = forms.CharField(max_length=100, required=False, label="Occupation")
    phone = forms.CharField(label="Mobile Phone", required=False)
    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES, required=True, label="Time Zone"
    )
    emotional_treatment_history = forms.CharField(
        required=False,
        label="Emotional Treatment",
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    medical_conditions = forms.MultipleChoiceField(
        choices=MEDICAL_CONDITIONS,
        required=False,
        label="Medical Conditions",
        widget=forms.CheckboxSelectMultiple,
    )
    fears_phobias = forms.CharField(
        required=False, label="Fears/Phobias", widget=forms.Textarea(attrs={"rows": 2})
    )
    referral_source = forms.ChoiceField(
        choices=REFERRAL_SOURCES, required=False, label="Referral Source"
    )
    referral_source_other = forms.CharField(
        required=False, label="Other Referral Source"
    )
    preferred_contact = forms.ChoiceField(
        choices=CONTACT_CHOICES, required=False, label="Preferred Contact Method"
    )
    notifications_enabled = forms.BooleanField(
        required=False, label="Enable Notifications"
    )
    avatar = forms.ImageField(required=False, label="Profile Picture")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.initial["first_name"] = self.instance.user.first_name
            self.initial["last_name"] = self.instance.user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            profile.save()
        return profile

    class Meta:
        model = Profile
        exclude = [
            "specialization",
            "therapy_consent",
            "bio",
            "is_coach",
            "is_client",
            "user",
            "last_login_ip",
            "google_refresh_token",
        ]
