from unittest import mock

from django.core.cache import cache
from django.db import connection
from django.test import TestCase
from django.urls import reverse

from MainApp.models import Problem
from UserContentCreation.views import _rate_limit_ok


class SolutionSubmissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # bulk_create skips Problem.save() (embedding model) on purpose:
        # these tests only exercise permissions and rate limiting.
        cls.problem = Problem.objects.bulk_create([Problem(title="T", slug="t")])[0]

    @mock.patch("resend.Emails.send")
    def test_submission_requires_login(self, _mail):
        response = self.client.post(reverse("SendSolution", args=[self.problem.pk]), {"solution": "hi"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/authentication/login/", response["Location"])

    @mock.patch("resend.Emails.send")
    def test_submission_rejects_empty_text(self, _mail):
        user = _make_user()
        self.client.force_login(user)
        response = self.client.post(reverse("SendSolution", args=[self.problem.pk]), {"solution": "   "})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be empty")


def _make_user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user("sol@example.com", "solsafe", "sturdy-Pass9!")


class RateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_blocks_after_five_submissions(self):
        results = [_rate_limit_ok(7) for _ in range(6)]
        self.assertEqual(results, [True, True, True, True, True, False])
