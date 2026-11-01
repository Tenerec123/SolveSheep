from django.test import TestCase
from django.urls import reverse


class RemovedEndpointsTests(TestCase):
    def test_ai_generation_route_removed(self):
        from django.urls.exceptions import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse("Create_Problem")
