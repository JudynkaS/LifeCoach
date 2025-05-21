from django.test import TestCase
from django.contrib.auth.models import User
from viewer.forms import SessionForm, ServiceForm, ReviewForm
from viewer.models import Service, Session
from accounts.models import Profile
from django.utils import timezone
import datetime


class SessionFormTest(TestCase):
    def setUp(self):
        self.coach_user = User.objects.create_user(
            username="coach", password="testpass123"
        )
        self.coach_profile = self.coach_user.profile
        self.coach_profile.is_coach = True
        self.coach_profile.save()

        self.client_user = User.objects.create_user(
            username="client", password="testpass123"
        )
        self.client_profile = self.client_user.profile
        self.client_profile.is_client = True
        self.client_profile.save()

        self.service = Service.objects.create(
            name="Life Coaching Session",
            price=100.00,
            duration=60,
            coach=self.coach_user,
        )

    def test_session_form_valid_data(self):
        form_data = {
            "service": self.service.id,
            "date_time": "2024-05-01T14:00",
            "type": "online",
            "notes": "Test session",
            "meeting_url": "https://meet.google.com/test",
            "meeting_address": "Test Address",
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_no_data(self):
        form = SessionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # service, date_time, type are required


class ServiceFormTest(TestCase):
    def test_service_form_valid_data(self):
        form_data = {
            "name": "Career Coaching",
            "description": "Career guidance and planning",
            "price": 150.00,
            "duration": 90,
            "is_active": True,
            "currency": "USD",
            "session_type": "online",
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_service_form_no_data(self):
        form = ServiceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            len(form.errors), 6
        )  # name, description, price, duration, currency, session_type are required


class ReviewFormTest(TestCase):
    def setUp(self):
        self.coach_user = User.objects.create_user(
            username="coach", password="testpass123"
        )
        self.coach_profile = self.coach_user.profile
        self.coach_profile.is_coach = True
        self.coach_profile.save()

        self.client_user = User.objects.create_user(
            username="client", password="testpass123"
        )
        self.client_profile = self.client_user.profile
        self.client_profile.is_client = True
        self.client_profile.save()

        self.service = Service.objects.create(
            name="Life Coaching Session",
            price=100.00,
            duration=60,
            coach=self.coach_user,
        )

        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type="online",
            date_time=timezone.now() + datetime.timedelta(days=1),
            duration=60,
            meeting_url="https://meet.google.com/test",
        )

    def test_review_form_valid_data(self):
        form_data = {
            "session": self.session.id,
            "rating": 5,
            "comment": "Excellent session!",
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form_data = {
            "session": self.session.id,
            "rating": 6,  # Rating should be between 1 and 5
            "comment": "Great session!",
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)
