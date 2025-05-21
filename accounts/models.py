from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model, OneToOneField, CASCADE, DateField, \
    TextField, ManyToManyField
import pytz

CONTACT_CHOICES = [
    ('email', 'Email'),
    ('phone', 'Phone'),
    ('both', 'Both Email and Phone')
]

TIMEZONE_CHOICES = [(tz, tz) for tz in pytz.all_timezones]

PHONE_PREFIXES = [
    ('+1', 'United States (+1)'),
    ('+420', 'Czech Republic (+420)'),
    ('+421', 'Slovakia (+421)'),
    ('+48', 'Poland (+48)'),
    ('+49', 'Germany (+49)'),
    ('+43', 'Austria (+43)'),
    ('+36', 'Hungary (+36)'),
]

SPECIALIZATION_CHOICES = [
    ('personal_development', 'Personal Development'),
    ('career_growth', 'Career Growth'),
    ('life_balance', 'Life Balance'),
    ('stress_management', 'Stress Management'),
    ('relationships', 'Relationships'),
    ('self_confidence', 'Self Confidence'),
]

GOALS_CHOICES = [
    ('improve_communication', 'Improve Communication'),
    ('career_direction', 'Find Career Direction'),
    ('boost_confidence', 'Boost Self-Confidence'),
    ('time_management', 'Better Time Management'),
    ('stress_handling', 'Stress Management'),
]

MARITAL_STATUS_CHOICES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
]


MEDICAL_CONDITIONS = [
    ('diabetes', 'Diabetes'),
    ('epilepsy', 'Epilepsy'),
    ('heart_disorder', 'Heart Disorder'),
    ('digestive_problems', 'Digestive Problems'),
]

REFERRAL_SOURCES = [
    ('medical_referral', 'Medical Referral'),
    ('relative', 'Relative'),
    ('friend', 'Friend'),
    ('newspaper', 'Newspaper'),
    ('radio', 'Radio'),
    ('television', 'Television'),
    ('phone_book', 'Phone Book'),
    ('other', 'Other'),
]

class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    date_of_birth = DateField(null=True, blank=True)
    phone = TextField(null=True, blank=True)
    bio = TextField(null=True, blank=True)
    timezone = models.CharField(max_length=50, choices=TIMEZONE_CHOICES, default='UTC')
    preferred_contact = models.CharField(max_length=20, choices=CONTACT_CHOICES, default='email')
    notifications_enabled = models.BooleanField(default=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_coach = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    
    # Fields for specialization and goals
    specialization = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name='Specialization'
    )

    # Personal Information
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], blank=True, null=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True, null=True)
    occupation = models.CharField(max_length=100, blank=True, null=True)

    # Medical History
    emotional_treatment_history = models.TextField(blank=True, null=True)
    medical_conditions = models.JSONField(default=list, blank=True, null=True)
    hypnosis_experience = models.TextField(blank=True, null=True)
    
    # Goals and Concerns
    hypnosis_goals = models.TextField(blank=True, null=True)
    previous_solution_attempts = models.TextField(blank=True, null=True)
    fears_phobias = models.TextField(blank=True, null=True)
    
    # Referral Information
    referral_source = models.CharField(max_length=50, choices=REFERRAL_SOURCES, blank=True, null=True)
    referral_source_other = models.CharField(max_length=100, blank=True, null=True)

    # Consent
    therapy_consent = models.BooleanField(default=False)
    hypnotherapy_consent = models.BooleanField(default=False)

    # Google refresh token
    google_refresh_token = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['user__username']

    def __repr__(self):
        return f"Profile(user={self.user})"

    def __str__(self):
        return self.user.username

    def get_timezone(self):
        return pytz.timezone(self.timezone)

    def set_last_login_ip(self, ip_address):
        self.last_login_ip = ip_address
        self.save()

    def get_goals_list(self):
        """Returns goals as a list."""
        return self.goals.split(',') if self.goals else []

    def set_goals_list(self, goals_list):
        """Sets goals from a list."""
        self.goals = ','.join(goals_list) if goals_list else ''

    def generate_bio(self):
        """Generates bio based on specialization."""
        parts = []
        if self.specialization:
            parts.append(f"I specialize in {self.specialization}.")
        return " ".join(parts) if parts else ""

    def get_medical_conditions(self):
        """Returns medical conditions as a list."""
        return self.medical_conditions or []

    def set_medical_conditions(self, conditions):
        """Sets medical conditions from a list."""
        self.medical_conditions = conditions if conditions else []