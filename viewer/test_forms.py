from django.test import TestCase
from django.contrib.auth.models import User
from viewer.forms import SessionForm, ServiceForm, ReviewForm
from viewer.models import Service, Session
from accounts.models import Profile

class SessionFormTest(TestCase):
    def setUp(self):
        self.coach_user = User.objects.create_user(username='coach', password='testpass123')
        self.coach_profile = Profile.objects.create(user=self.coach_user, is_coach=True)
        
        self.client_user = User.objects.create_user(username='client', password='testpass123')
        self.client_profile = Profile.objects.create(user=self.client_user, is_client=True)
        
        self.service = Service.objects.create(
            name='Life Coaching Session',
            price=100.00,
            duration=60
        )

    def test_session_form_valid_data(self):
        form_data = {
            'client': self.client_profile.id,
            'coach': self.coach_profile.id,
            'service': self.service.id,
            'type': 'online',
            'date': '2024-05-01',
            'time': '14:00'
        }
        form = SessionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_session_form_no_data(self):
        form = SessionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 6)

class ServiceFormTest(TestCase):
    def test_service_form_valid_data(self):
        form_data = {
            'name': 'Career Coaching',
            'description': 'Career guidance and planning',
            'price': 150.00,
            'duration': 90,
            'is_active': True,
            'currency': 'USD'
        }
        form = ServiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_service_form_no_data(self):
        form = ServiceForm(data={})
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 3)  # name, price, duration are required

class ReviewFormTest(TestCase):
    def setUp(self):
        self.coach_user = User.objects.create_user(username='coach', password='testpass123')
        self.coach_profile = Profile.objects.create(user=self.coach_user, is_coach=True)
        
        self.client_user = User.objects.create_user(username='client', password='testpass123')
        self.client_profile = Profile.objects.create(user=self.client_user, is_client=True)
        
        self.service = Service.objects.create(
            name='Life Coaching Session',
            price=100.00,
            duration=60
        )
        
        self.session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            type='online'
        )

    def test_review_form_valid_data(self):
        form_data = {
            'session': self.session.id,
            'rating': 5,
            'comment': 'Excellent session!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_review_form_invalid_rating(self):
        form_data = {
            'session': self.session.id,
            'rating': 6,  # Rating should be between 1 and 5
            'comment': 'Great session!'
        }
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors) 