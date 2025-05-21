from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import Profile
from .models import Service, Session, Payment, PaymentMethod
from django.utils import timezone
import datetime


class ViewerTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Vytvoření testovacího klienta
        self.client_user = User.objects.create_user(
            username="client", email="client@example.com", password="clientpass123"
        )
        self.client_profile = self.client_user.profile
        self.client_profile.is_client = True
        self.client_profile.timezone = "UTC"
        self.client_profile.save()

        # Vytvoření testovacího kouče
        self.coach_user = User.objects.create_user(
            username="coach", email="coach@example.com", password="coachpass123"
        )
        self.coach_profile = self.coach_user.profile
        self.coach_profile.is_coach = True
        self.coach_profile.timezone = "UTC"
        self.coach_profile.save()

        # Vytvoření testovací služby
        self.service = Service.objects.create(
            name="Test Service",
            description="Test Description",
            price=100.00,
            duration=60,
            currency="USD",
            is_active=True,
            coach=self.coach_user,
        )

    def test_service_list_view(self):
        """Test zobrazení seznamu služeb"""
        response = self.client.get(reverse("viewer:services"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "viewer/service_list.html")
        self.assertContains(response, "Test Service")

    def test_booking_creation(self):
        """Test vytvoření rezervace"""
        self.client.login(username="client", password="clientpass123")

        # Test vytvoření rezervace
        future_date = timezone.now() + datetime.timedelta(days=1)
        payment_method = PaymentMethod.objects.create(name="paypal")
        response = self.client.post(
            reverse("viewer:booking_create"),
            {
                "service": self.service.id,
                "date_time": future_date.strftime("%Y-%m-%d %H:%M"),
                "type": "online",
                "notes": "Test notes",
                "payment_method": payment_method.id,
                "duration": 60,
                "meeting_url": "https://meet.test/session",
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Přesměrování po úspěšném vytvoření

        # Ověření, že rezervace byla vytvořena
        self.assertTrue(
            Session.objects.filter(
                client=self.client_profile, service=self.service
            ).exists()
        )

    def test_session_edit(self):
        """Test editace rezervace"""
        # Vytvoření testovací rezervace
        session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            date_time=timezone.now() + datetime.timedelta(days=2),
            type='online',
            status='CONFIRMED',
            duration=60,
            meeting_url='https://meet.test/session'
        )
        
        # Vytvoření platby pro tuto session
        payment_method = PaymentMethod.objects.create(name='paypal')
        Payment.objects.create(
            session=session,
            amount=self.service.price,
            payment_method=payment_method
        )
        
        self.client.login(username='client', password='clientpass123')
        
        # Test editace rezervace
        new_date = timezone.now() + datetime.timedelta(days=3)
        response = self.client.post(
            reverse('viewer:session_edit', args=[session.id]),
            {
                'date_time': new_date.strftime('%Y-%m-%d %H:%M'),
                'notes': 'Updated notes',
                'type': session.type,
                'duration': session.duration,
                'service': session.service.id,
                'meeting_url': 'https://meet.test/updated',
                'meeting_address': 'Updated Address',
                'payment_method': payment_method.id
            }
        )
        if response.status_code != 302:
            print('Form errors:', response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        
        # Ověření změn
        updated_session = Session.objects.get(id=session.id)
        self.assertEqual(updated_session.notes, 'Updated notes')

    def test_session_cancellation(self):
        """Test zrušení rezervace"""
        # Vytvoření testovací rezervace
        session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            date_time=timezone.now() + datetime.timedelta(days=2),
            type="online",
            status="CONFIRMED",
            duration=60,
        )

        self.client.login(username="client", password="clientpass123")

        # Test zrušení rezervace
        response = self.client.post(reverse("viewer:cancel_session", args=[session.id]))
        self.assertEqual(response.status_code, 302)

        # Ověření, že rezervace byla zrušena
        updated_session = Session.objects.get(id=session.id)
        self.assertEqual(updated_session.status, "CANCELLED")

    def test_payment_creation(self):
        """Test vytvoření platby"""
        # Vytvoření testovací rezervace
        session = Session.objects.create(
            client=self.client_profile,
            coach=self.coach_profile,
            service=self.service,
            date_time=timezone.now() + datetime.timedelta(days=2),
            type="online",
            status="CONFIRMED",
            duration=60,
        )

        # Test vytvoření platby
        payment_method = PaymentMethod.objects.create(name="paypal")
        payment = Payment.objects.create(
            session=session, amount=self.service.price, payment_method=payment_method
        )

        self.assertTrue(Payment.objects.filter(session=session).exists())
        self.assertEqual(payment.amount, self.service.price)

    def test_report_generation(self):
        """Test generování reportů"""
        self.client.login(username="coach", password="coachpass123")

        # Vytvoření testovacích rezervací
        for i in range(3):
            Session.objects.create(
                client=self.client_profile,
                coach=self.coach_profile,
                service=self.service,
                date_time=timezone.now() + datetime.timedelta(days=i),
                type="online",
                status="CONFIRMED",
                duration=60,
            )

        # Test zobrazení reportu
        response = self.client.get(reverse("viewer:coach_report"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "viewer/coach_report.html")
        self.assertContains(response, "Test Service")
