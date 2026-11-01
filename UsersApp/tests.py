import time
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


def make_inactive_user():
    # UserManager.create_user does not force is_active=False (only the
    # Register view does), so set it explicitly, as Register would.
    user = User.objects.create_user("user@example.com", "tester", "s3cretPass!123")
    user.is_active = False
    user.save()
    return user


class ActivationTests(TestCase):
    def test_activate_marks_user_active_and_logs_in(self):
        user = make_inactive_user()
        token = signing.TimestampSigner().sign(user.pk)

        response = self.client.get(reverse("Activate", args=[token]), follow=True)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_invalid_token_redirects_to_register(self):
        response = self.client.get(reverse("Activate", args=["forged-token"]))
        self.assertRedirects(response, reverse("Register"), fetch_redirect_response=False)

    def test_expired_token_is_rejected(self):
        user = make_inactive_user()
        # Sign with a clock more than 48h in the past, then restore the real
        # clock so the view (and unsign's max_age check) sees 'now'.
        with mock.patch("django.core.signing.time.time", return_value=time.time() - 200_000):
            token = signing.TimestampSigner().sign(user.pk)

        response = self.client.get(reverse("Activate", args=[token]))

        user.refresh_from_db()
        self.assertFalse(user.is_active)
        self.assertRedirects(response, reverse("Register"), fetch_redirect_response=False)


class RegisterTests(TestCase):
    @mock.patch("resend.Emails.send")
    def test_register_creates_inactive_user_and_sends_mail_to_the_user(self, send_email):
        response = self.client.post(reverse("Register"), {
            "email": "newuser@example.com",
            "username": "newbie",
            "password1": "sturdy-Pass9!",
            "password2": "sturdy-Pass9!",
        })

        user = User.objects.get(username="newbie")
        self.assertFalse(user.is_active)
        message = send_email.call_args.args[0]
        self.assertEqual(message["to"], user.email)
        self.assertIn("activate", message["html"].lower())
