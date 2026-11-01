from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from MainApp.models import Problem

User = get_user_model()


class LikeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # bulk_create skips Problem.save() (embedding model) on purpose.
        cls.problem = Problem.objects.bulk_create([Problem(title="T", slug="t")])[0]
        cls.user = User.objects.create_user("like@example.com", "liker", "sturdy-Pass9!")

    def test_like_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        response = client.post(reverse("Like", args=[self.problem.slug]))
        self.assertEqual(response.status_code, 403)

    def test_like_toggles_and_keeps_count_consistent(self):
        client = Client()
        client.force_login(self.user)
        response = client.post(reverse("Like", args=[self.problem.slug]))
        self.assertEqual(response.json(), {"likes_count": 1, "liked": True})
        response = client.post(reverse("Like", args=[self.problem.slug]))
        self.assertEqual(response.json(), {"likes_count": 0, "liked": False})

