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
            existing_class = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing_class + " form-control").strip()


class SessionForm(BaseStyledForm):
    class Meta:
        model = Session
        fields = [
            "service",
            "date_time",
            "type",
            "notes",
            "meeting_url",
            "meeting_address",
        ]
        widgets = {
            "date_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "meeting_url": forms.URLInput(attrs={"placeholder": "https://..."}),
            "meeting_address": forms.TextInput(
                attrs={"placeholder": "Address for personal session"}
            ),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Pro kouče: pouze některá pole editovatelná
            if user and hasattr(user, "profile") and user.profile.is_coach:
                # Nastavit readonly pro všechna pole kromě date_time, meeting_url a meeting_address
                readonly_fields = ["service", "type", "notes"]
                for field in readonly_fields:
                    if field in self.fields:
                        self.fields[field].disabled = True
                        self.fields[field].widget.attrs["readonly"] = True
            # Pro klienta: vše readonly pokud je méně než 24h do začátku
            elif user and hasattr(user, "profile") and user.profile.is_client:
                if (
                    self.instance.date_time
                    and (self.instance.date_time - timezone.now()).total_seconds()
                    < 24 * 60 * 60
                ):
                    for field in self.fields:
                        self.fields[field].disabled = True
                        self.fields[field].widget.attrs["readonly"] = True
                else:
                    # Pokud je více než 24h, může měnit pouze date_time a notes
                    readonly_fields = [
                        "service",
                        "type",
                        "meeting_url",
                        "meeting_address",
                    ]
                    for field in readonly_fields:
                        if field in self.fields:
                            self.fields[field].disabled = True
                            self.fields[field].widget.attrs["readonly"] = True

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        date_time = cleaned_data.get("date_time")
        if service and date_time:
            start = date_time
            end = date_time + timezone.timedelta(minutes=service.duration)

            def overlaps(qs, who):
                qs = qs.filter(status__in=["CONFIRMED", "PENDING"])
                if self.instance and self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                for s in qs:
                    s_start = s.date_time
                    s_end = s.date_time + timezone.timedelta(minutes=s.duration)
                    if (start < s_end) and (end > s_start):
                        raise forms.ValidationError(
                            f"{who} already has a session that overlaps with this time. (Termín je již obsazený)"
                        )

            overlaps(Session.objects.filter(coach=service.coach.profile), "This coach")
            if hasattr(self, "user") and self.user and hasattr(self.user, "profile"):
                overlaps(Session.objects.filter(client=self.user.profile), "You")
        return cleaned_data


class ServiceForm(BaseStyledForm):
    class Meta:
        model = Service
        fields = [
            "name",
            "description",
            "price",
            "duration",
            "currency",
            "session_type",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": 0, "step": 0.01}),
            "duration": forms.NumberInput(attrs={"min": 15, "step": 15}),
        }


class ReviewForm(BaseStyledForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get("rating")
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating


class BookingForm(BaseStyledForm):
    date_time = forms.CharField(
        label="Date time*",
        widget=forms.Select(attrs={"class": "form-control"}),
        required=True,
        error_messages={
            "required": "Please select a date and time.",
            "invalid": "Please select a valid date and time from the available slots.",
        },
    )
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.all(),
        label="Payment Method*",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    type = forms.ChoiceField(
        choices=[("online", "Online"), ("personal", "Personal")],
        label="Session Type*",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        label="Additional Notes",
    )

    class Meta:
        model = Session
        fields = [
            "service",
            "date_time",
            "type",
            "notes",
            "meeting_url",
            "meeting_address",
        ]
        widgets = {
            "service": forms.Select(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
            "meeting_url": forms.URLInput(
                attrs={"placeholder": "https://...", "class": "form-control"}
            ),
            "meeting_address": forms.TextInput(
                attrs={
                    "placeholder": "Address for personal session",
                    "class": "form-control",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Get user's timezone
        user_timezone = timezone.get_current_timezone()
        if self.user and hasattr(self.user, "profile") and self.user.profile.timezone:
            try:
                user_timezone = pytz.timezone(self.user.profile.timezone)
            except pytz.exceptions.UnknownTimeZoneError:
                pass

        # Set up service choices
        if self.user and hasattr(self.user, "profile"):
            if self.user.profile.is_coach:
                self.fields["service"].queryset = Service.objects.filter(
                    coach=self.user, is_active=True
                )
            else:
                self.fields["service"].queryset = Service.objects.filter(is_active=True)

        # Pokud editujeme existující session, předvyplň date_time i když není mezi sloty
        if self.instance and self.instance.pk and self.instance.date_time:
            dt = self.instance.date_time.astimezone(user_timezone)
            dt_str = dt.strftime("%Y-%m-%d %H:%M")
            # Pokud není mezi choices, přidej ji na začátek
            choices = list(self.fields["date_time"].widget.choices)
            if not any(val == dt_str for val, _ in choices):
                display = dt.strftime("%d.%m.%Y %H:%M")
                choices.insert(0, (dt_str, display))
                self.fields["date_time"].widget.choices = choices
            self.initial["date_time"] = dt_str

        # Ostatní readonly logika zůstává
        if self.instance and self.instance.pk:
            session_time = self.instance.date_time.astimezone(user_timezone)
            now = timezone.now().astimezone(user_timezone)
            if (
                self.user
                and hasattr(self.user, "profile")
                and self.user.profile.is_client
            ):
                time_until_session = session_time - now
                if time_until_session.total_seconds() < 24 * 60 * 60:
                    for field in self.fields:
                        self.fields[field].disabled = True
                        self.fields[field].widget.attrs["readonly"] = True
                else:
                    readonly_fields = [
                        "service",
                        "type",
                        "meeting_url",
                        "meeting_address",
                    ]
                    for field in readonly_fields:
                        if field in self.fields:
                            self.fields[field].disabled = True
                            self.fields[field].widget.attrs["readonly"] = True

    def clean_date_time(self):
        date_time_str = self.cleaned_data.get("date_time")
        if not date_time_str:
            raise forms.ValidationError("Please select a date and time.")

        try:
            # Try parsing the date in the expected format from the select field
            date_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
            date_time = timezone.make_aware(date_time)

            # Get user's timezone
            user_timezone = timezone.get_current_timezone()
            if (
                self.user
                and hasattr(self.user, "profile")
                and self.user.profile.timezone
            ):
                try:
                    user_timezone = pytz.timezone(self.user.profile.timezone)
                except pytz.exceptions.UnknownTimeZoneError:
                    pass

            # Convert the date_time to user's timezone for comparison
            date_time_local = date_time.astimezone(user_timezone)
            now_local = timezone.now().astimezone(user_timezone)

            # Check if the selected time is in the future
            if date_time_local <= now_local:
                raise forms.ValidationError("Please select a future date and time.")

            return date_time
        except ValueError:
            raise forms.ValidationError(
                "Invalid date/time format. Please select from the available options."
            )

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        date_time = cleaned_data.get("date_time")

        if service and date_time:
            # Check for overlapping sessions
            start = date_time
            end = date_time + timezone.timedelta(minutes=service.duration)

            # Helper for overlap: (A starts before B ends) and (A ends after B starts)
            def overlaps(qs, who):
                qs = qs.filter(status__in=["CONFIRMED", "PENDING"])
                if self.instance and self.instance.pk:
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
            if self.user and hasattr(self.user, "profile"):
                overlaps(Session.objects.filter(client=self.user.profile), "You")

        return cleaned_data
