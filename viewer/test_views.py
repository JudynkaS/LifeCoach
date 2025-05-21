from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from viewer.models import Service, Session, Review
from accounts.models import Profile
from django.utils import timezone
import datetime
from viewer.models import PaymentMethod


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create users and profiles
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

        # Create a service
        self.service = Service.objects.create(
            name="Life Coaching Session",
            description="One-on-one coaching session",
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
            duration=60,
            date_time=timezone.now() + datetime.timedelta(days=20),
        )

    def test_home_view(self):
        response = self.client.get(reverse("viewer:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_service_list_view(self):
        response = self.client.get(reverse("viewer:services"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "viewer/service_list.html")
        self.assertContains(response, "Life Coaching Session")

    def test_service_detail_view(self):
        response = self.client.get(
            reverse("viewer:service_detail", args=[self.service.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "viewer/service_detail.html")
        self.assertContains(response, self.service.name)

    def test_session_list_view_authenticated(self):
        self.client.login(username="client", password="testpass123")
        response = self.client.get(reverse("viewer:session_history"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "viewer/session_history.html")

    def test_session_list_view_unauthenticated(self):
        response = self.client.get(reverse("viewer:session_history"))
        self.assertEqual(response.status_code, 302)  # Redirects to login

    def test_session_create_view(self):
        self.client.login(username="client", password="testpass123")
        payment_method = PaymentMethod.objects.create(name="paypal")
        future_date = (timezone.now() + datetime.timedelta(days=10)).strftime(
            "%Y-%m-%d %H:%M"
        )
        form_data = {
            "service": self.service.id,
            "date_time": future_date,
            "type": "online",
            "duration": 60,
            "meeting_url": "https://meet.google.com/test",
            "meeting_address": "Test Address",
            "payment_method": payment_method.id,
            "notes": "Test notes",
        }
        response = self.client.post(reverse("viewer:booking_create"), data=form_data)
        if response.status_code != 302:
            print("Form errors:", response.context["form"].errors)
        self.assertEqual(
            response.status_code, 302
        )  # Redirects after successful creation
        self.assertTrue(Session.objects.filter(client=self.client_profile).exists())

    def test_review_create_view(self):
        self.client.login(username="client", password="testpass123")
        form_data = {
            "session": self.session.id,
            "rating": 5,
            "comment": "Excellent session!",
        }
        response = self.client.post(
            reverse("viewer:create-review", args=[self.session.id]), data=form_data
        )
        self.assertEqual(
            response.status_code, 302
        )  # Redirects after successful creation
        self.assertTrue(Review.objects.filter(session=self.session).exists())

    def test_session_edit(self):
        self.client.login(username='client', password='testpass123')
        payment_method = PaymentMethod.objects.create(name='paypal')
        # Vytvořím platbu pro self.session
        from viewer.models import Payment
        Payment.objects.create(
            session=self.session,
            amount=self.service.price,
            payment_method=payment_method
        )
        print('Payment methods:', list(PaymentMethod.objects.all()))
        print('Payments for session:', list(self.session.payments.all()))
        future_date = (timezone.now() + datetime.timedelta(days=11)).strftime('%Y-%m-%d %H:%M')
        form_data = {
            'service': self.service.id,
            'date_time': future_date,
            'type': 'online',
            'duration': 60,
            'meeting_url': 'https://meet.google.com/test',
            'meeting_address': 'Test Address',
            'payment_method': payment_method.id,
            'notes': 'Updated notes'
        }
        response = self.client.post(
            reverse('viewer:session_edit', kwargs={'pk': self.session.id}),
            data=form_data
        )
        if response.status_code != 302:
            print('Form errors:', response.context['form'].errors)
            print('Form payment_method queryset:', list(response.context['form'].fields['payment_method'].queryset))
        self.assertEqual(response.status_code, 302)
        self.session.refresh_from_db()
        self.assertEqual(self.session.notes, 'Updated notes')

    # def test_coach_list_view(self):
    #     response = self.client.get(reverse('viewer:coach-list'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'coach_list.html')
    #     self.assertContains(response, 'coach')  # Username of the coach

    # def test_coach_detail_view(self):
    #     response = self.client.get(reverse('viewer:coach-detail', args=[self.coach_profile.id]))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTemplateUsed(response, 'coach_detail.html')
    #     self.assertContains(response, self.coach_user.username)
