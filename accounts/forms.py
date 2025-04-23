from django.contrib.auth.forms import UserCreationForm
from django.db.transaction import atomic
from django.forms import CharField, PasswordInput, DateField, NumberInput, \
    Textarea, ModelForm

from accounts.models import Profile


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name', 'email',
                  'password1', 'password2']

        labels = {
            'username': 'Username',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
        }

    password1 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Password'}),
        label='Password'
    )

    password2 = CharField(
        widget=PasswordInput(attrs={'placeholder': 'Password again'}),
        label='Password again'
    )

    phone = CharField(
        label='Phone Number',
        required=False
    )

    @atomic
    def save(self, commit=True):
        self.instance.is_active = True
        user = super().save(commit)

        date_of_birth = self.cleaned_data.get('date_of_birth')
        biography = self.cleaned_data.get('biography')
        phone = self.cleaned_data.get('phone')
        profile = Profile(
            user=user,
            date_of_birth=date_of_birth,
            biography=biography,
            phone=phone
        )
        if commit:
            profile.save()
        return user


class ProfileUpdateForm(ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'timezone', 'bio', 'preferred_contact']
        labels = {
            'phone': 'Phone Number',
            'timezone': 'Time Zone',
            'bio': 'Biography',
            'preferred_contact': 'Preferred Contact Method'
        }
        widgets = {
            'bio': Textarea(attrs={'rows': 4}),
        }
