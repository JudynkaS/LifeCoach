from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile
from django.core.files.uploadedfile import SimpleUploadedFile
import os


class AccountsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Vytvoření testovacího uživatele
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.profile = self.user.profile
        self.profile.phone = "123456789"
        self.profile.timezone = "UTC"
        self.profile.bio = "Test bio"
        self.profile.preferred_contact = "email"
        self.profile.notifications_enabled = True
        self.profile.is_client = True
        self.profile.save()

    def test_registration_view(self):
        """Test registračního formuláře"""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

        # Test úspěšné registrace
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password1": "testpass123",
                "password2": "testpass123",
                "first_name": "New",
                "last_name": "User",
                "street_address": "Test Street 123",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "12345",
                "date_of_birth": "1990-01-01",
                "sex": "M",
                "phone_prefix": "+1",
                "phone": "987654321",
                "timezone": "UTC",
                "preferred_contact": "email",
                "is_client": True,
                "therapy_consent": True,
            },
        )
        self.assertEqual(
            response.status_code, 302
        )  # Přesměrování po úspěšné registraci
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_view(self):
        """Test přihlašovacího formuláře"""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

        # Test úspěšného přihlášení
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "testuser", "password": "testpass123"},
        )
        self.assertEqual(
            response.status_code, 302
        )  # Přesměrování po úspěšném přihlášení

    def test_profile_view(self):
        """Test zobrazení profilu"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(
            reverse("accounts:profile", kwargs={"pk": self.profile.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_edit(self):
        """Test editace profilu"""
        self.client.login(username="testuser", password="testpass123")

        # Test úspěšné editace
        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "Updated",
                "last_name": "Name",
                "street_address": "Updated Street 123",
                "city": "Updated City",
                "state": "Updated State",
                "zip_code": "54321",
                "date_of_birth": "1990-01-01",
                "sex": "M",
                "phone_prefix": "+1",
                "phone": "999888777",
                "timezone": "Europe/Prague",
                "bio": "Updated bio",
                "preferred_contact": "phone",
                "is_client": True,
                "therapy_consent": True,
            },
        )
        self.assertEqual(response.status_code, 302)  # Přesměrování po úspěšné editaci

        # Ověření změn
        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.phone, "999888777")
        self.assertEqual(updated_profile.timezone, "Europe/Prague")

    def test_avatar_upload(self):
        """Test nahrávání avatara"""
        self.client.login(username="testuser", password="testpass123")

        # Vytvoření testovacího obrázku s validním obsahem
        image_content = (
            b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
            b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
            b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
        )
        image = SimpleUploadedFile(
            name="test_image.gif", content=image_content, content_type="image/gif"
        )

        response = self.client.post(
            reverse("accounts:profile_edit"),
            {
                "first_name": "Test",
                "last_name": "User",
                "street_address": "Test Street 123",
                "city": "Test City",
                "state": "Test State",
                "zip_code": "12345",
                "date_of_birth": "1990-01-01",
                "sex": "M",
                "phone_prefix": "+1",
                "phone": "123456789",
                "timezone": "UTC",
                "avatar": image,
                "is_client": True,
                "therapy_consent": True,
            },
        )
        self.assertEqual(response.status_code, 302)

        # Ověření, že avatar byl nahrán
        updated_profile = Profile.objects.get(user=self.user)
        self.assertTrue(updated_profile.avatar)

    def test_password_change(self):
        """Test změny hesla"""
        self.client.login(username="testuser", password="testpass123")

        # Test GET požadavku na stránku změny hesla
        response = self.client.get(reverse("accounts:password_change"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/password_change.html")

        # Test POST požadavku pro změnu hesla
        response = self.client.post(
            reverse("accounts:password_change"),
            {
                "old_password": "testpass123",
                "new_password1": "newpass123",
                "new_password2": "newpass123",
            },
        )
        self.assertEqual(response.status_code, 302)  # Očekáváme přesměrování

        # Ověření, že jsme byli přesměrováni na stránku potvrzení změny hesla
        self.assertRedirects(response, reverse("accounts:password_change_done"))

        # Ověření, že se lze přihlásit s novým heslem
        self.client.logout()
        login_successful = self.client.login(username="testuser", password="newpass123")
        self.assertTrue(login_successful)
