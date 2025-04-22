from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.db.transaction import atomic
from django.forms import CharField, PasswordInput, Textarea

from accounts.models import Profile

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

        labels = {
            'username': 'Uživatelské jméno',
            'first_name': 'Jméno',
            'last_name': 'Příjmení',
            'email': 'E-mail',
        }

    password1 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Heslo'}),
        label='Heslo'
    )

    password2 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Heslo znovu'}),
        label='Heslo znovu'
    )

    phone = CharField(
        label='Telefonní číslo',
        required=False
    )

    bio = CharField(
        widget=Textarea,
        label='Biografie',
        required=False
    )

    @atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True
        user.is_client = True
        if commit:
            user.save()

        phone = self.cleaned_data.get('phone')
        bio = self.cleaned_data.get('bio')

        Profile.objects.create(
            user=user,
            phone=phone,
            bio=bio,
            is_client=True
        )
        return user
