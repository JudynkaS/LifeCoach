from django.test import TestCase
from django.contrib.auth.models import User
from viewer.models import Service, Session, Review
from accounts.models import Profile
from django.utils import timezone
import datetime


class ServiceModelTest(TestCase):
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

    def test_service_creation(self):
        self.assertTrue(isinstance(self.service, Service))
        self.assertEqual(str(self.service), "Life Coaching Session")


class SessionModelTest(TestCase):
    def setUp(self):
        # Create a coach user
        self.coach_user = User.objects.create_user(
            username="coach", password="testpass123"
        )
        self.coach_profile = self.coach_user.profile
        self.coach_profile.is_coach = True
        self.coach_profile.save()

        # Create a client user
        self.client_user = User.objects.create_user(
            username="client", password="testpass123"
        )
        self.client_profile = self.client_user.profile
        self.client_profile.is_client = True
        self.client_profile.save()

        # Create a service
        self.service = Service.objects.create(
            name="Life Coaching Session",
            price=100.00,
            duration=60,
            coach=self.coach_user,
        )

        # Create a session
        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type="online",
            date_time=timezone.now() + datetime.timedelta(days=1),
            duration=60,
            meeting_url="https://meet.google.com/test",
        )

    def test_session_creation(self):
        self.assertTrue(isinstance(self.session, Session))
        self.assertEqual(self.session.client, self.client_profile)
        self.assertEqual(self.session.coach, self.coach_profile)


class ReviewModelTest(TestCase):
    def setUp(self):
        # Create a client user
        self.client_user = User.objects.create_user(
            username="client", password="testpass123"
        )
        self.client_profile = self.client_user.profile
        self.client_profile.is_client = True
        self.client_profile.save()

        # Create a coach user
        self.coach_user = User.objects.create_user(
            username="coach", password="testpass123"
        )
        self.coach_profile = self.coach_user.profile
        self.coach_profile.is_coach = True
        self.coach_profile.save()

        # Create a service
        self.service = Service.objects.create(
            name="Life Coaching Session",
            price=100.00,
            duration=60,
            coach=self.coach_user,
        )

        # Create a session s povinnými poli
        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type="online",
            date_time=timezone.now() + datetime.timedelta(days=1),
            duration=60,
            meeting_url="https://meet.google.com/test",
        )

        # Create a review
        self.review = Review.objects.create(
            session=self.session, rating=5, comment="Great session!"
        )

    def test_review_creation(self):
        self.assertTrue(isinstance(self.review, Review))
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Great session!")
