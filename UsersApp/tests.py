import time
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import signing
from django.test import Client, TestCase
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


class OwnerProgressVisibilityTests(TestCase):
    def test_problem_progress_is_visible_only_on_its_owners_profile(self):
        from MainApp.models import Problem, ProblemProgress

        owner = User.objects.create_user("owner@example.com", "owner", "sturdy-Pass9!")
        problem = Problem.objects.bulk_create([
            Problem(title="Private progress item", slug="private-progress-item")
        ])[0]
        ProblemProgress.objects.create(user=owner, problem=problem, status="solved")

        self.client.force_login(owner)
        owner_response = self.client.get(
            reverse("UserInterface_problems", args=[owner.username])
        )
        self.assertContains(owner_response, 'data-problem-status="solved"')
        self.assertContains(owner_response, "Private progress item")
        self.assertContains(owner_response, "Solved")

        other_user = User.objects.create_user(
            "other@example.com", "other", "sturdy-Pass9!"
        )
        other_client = Client()
        other_client.force_login(other_user)
        other_response = other_client.get(
            reverse("UserInterface_problems", args=[owner.username])
        )
        self.assertEqual(other_response.status_code, 200)
        self.assertNotContains(other_response, "data-problem-status=")
        self.assertNotContains(other_response, "Private progress item")

        public_response = Client().get(
            reverse("UserInterface_problems", args=[owner.username])
        )
        self.assertEqual(public_response.status_code, 200)
        self.assertNotContains(public_response, "data-problem-status=")
        self.assertNotContains(public_response, "Private progress item")
