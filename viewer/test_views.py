from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from viewer.models import Service, Session, Review
from accounts.models import Profile

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users and profiles
        self.coach_user = User.objects.create_user(username='coach', password='testpass123')
        self.coach_profile = Profile.objects.create(user=self.coach_user, is_coach=True)
        
        self.client_user = User.objects.create_user(username='client', password='testpass123')
        self.client_profile = Profile.objects.create(user=self.client_user, is_client=True)
        
        # Create a service
        self.service = Service.objects.create(
            name='Life Coaching Session',
            description='One-on-one coaching session',
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

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_service_list_view(self):
        response = self.client.get(reverse('service-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service_list.html')
        self.assertContains(response, 'Life Coaching Session')

    def test_service_detail_view(self):
        response = self.client.get(reverse('service-detail', args=[self.service.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service_detail.html')
        self.assertContains(response, self.service.name)

    def test_session_list_view_authenticated(self):
        self.client.login(username='client', password='testpass123')
        response = self.client.get(reverse('session-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'session_list.html')

    def test_session_list_view_unauthenticated(self):
        response = self.client.get(reverse('session-list'))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_session_create_view(self):
        self.client.login(username='client', password='testpass123')
        form_data = {
            'coach': self.coach_profile.id,
            'service': self.service.id,
            'type': 'online',
            'date': '2024-05-01',
            'time': '14:00'
        }
        response = self.client.post(reverse('session-create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after successful creation
        self.assertTrue(Session.objects.filter(client=self.client_profile).exists())

    def test_review_create_view(self):
        self.client.login(username='client', password='testpass123')
        form_data = {
            'session': self.session.id,
            'rating': 5,
            'comment': 'Excellent session!'
        }
        response = self.client.post(reverse('review-create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirects after successful creation
        self.assertTrue(Review.objects.filter(session=self.session).exists())

    def test_coach_list_view(self):
        response = self.client.get(reverse('coach-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_list.html')
        self.assertContains(response, 'coach')  # Username of the coach

    def test_coach_detail_view(self):
        response = self.client.get(reverse('coach-detail', args=[self.coach_profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'coach_detail.html')
        self.assertContains(response, self.coach_user.username) 