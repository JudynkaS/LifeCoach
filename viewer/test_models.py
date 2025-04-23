from django.test import TestCase
from django.contrib.auth.models import User
from viewer.models import Service, Session, Review
from accounts.models import Profile

class ServiceModelTest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name='Life Coaching Session',
            description='One-on-one life coaching session',
            price=100.00,
            duration=60,
            is_active=True,
            currency='USD'
        )

    def test_service_creation(self):
        self.assertTrue(isinstance(self.service, Service))
        self.assertEqual(str(self.service), 'Life Coaching Session')

class SessionModelTest(TestCase):
    def setUp(self):
        # Create a coach user
        self.coach_user = User.objects.create_user(username='coach', password='testpass123')
        self.coach_profile = Profile.objects.create(user=self.coach_user, is_coach=True)
        
        # Create a client user
        self.client_user = User.objects.create_user(username='client', password='testpass123')
        self.client_profile = Profile.objects.create(user=self.client_user, is_client=True)
        
        # Create a service
        self.service = Service.objects.create(
            name='Life Coaching Session',
            price=100.00,
            duration=60
        )
        
        # Create a session
        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type='online'
        )

    def test_session_creation(self):
        self.assertTrue(isinstance(self.session, Session))
        self.assertEqual(self.session.client, self.client_profile)
        self.assertEqual(self.session.coach, self.coach_profile)

class ReviewModelTest(TestCase):
    def setUp(self):
        # Create a client user
        self.client_user = User.objects.create_user(username='client', password='testpass123')
        self.client_profile = Profile.objects.create(user=self.client_user, is_client=True)
        
        # Create a coach user
        self.coach_user = User.objects.create_user(username='coach', password='testpass123')
        self.coach_profile = Profile.objects.create(user=self.coach_user, is_coach=True)
        
        # Create a service
        self.service = Service.objects.create(
            name='Life Coaching Session',
            price=100.00,
            duration=60
        )
        
        # Create a session
        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type='online'
        )
        
        # Create a review
        self.review = Review.objects.create(
            session=self.session,
            rating=5,
            comment='Great session!'
        )

    def test_review_creation(self):
        self.assertTrue(isinstance(self.review, Review))
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Great session!') 