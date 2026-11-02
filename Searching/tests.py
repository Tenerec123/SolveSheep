from django.test import TestCase
from django.urls import reverse

from MainApp.models import DifTag, Problem, TypeTag


class SearchPresentationPreservationTests(TestCase):
    """Verify the existing GET filters still select the same problems while
    Search opts into the native-masonry presentation wrapper.
    """

    def test_type_filter_and_search_controls_remain_unchanged(self):
        invariant = TypeTag.objects.create(name="Invariant", color="#245A70")
        geometry = TypeTag.objects.create(name="Geometry", color="#D8794E")
        difficulty = DifTag.objects.create(name=1.0, color="#245A70")

        matching = Problem.objects.create(
            title="Search target invariant 784",
            text="Find the preserved filter result.",
            dif_tag=difficulty,
            embedding=[0.0] * 384,
        )
        matching.type_tags.add(invariant)
        excluded = Problem.objects.create(
            title="Excluded geometry 953",
            text="This problem has a different type tag.",
            dif_tag=difficulty,
            embedding=[0.0] * 384,
        )
        excluded.type_tags.add(geometry)

        response = self.client.get(reverse("Search"), {
            "Dif": "0",
            "Type": str(invariant.pk),
            "Text": "",
            "Range": "false",
            "Start_Dif": "0",
            "End_Dif": "0",
        })

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn(matching.title, html)
        self.assertNotIn(excluded.title, html)
        self.assertIn('name="Dif"', html)
        self.assertIn('name="Type"', html)
        self.assertIn('name="Text"', html)
        self.assertIn('name="Range"', html)
        self.assertIn('name="Start_Dif"', html)
        self.assertIn('name="End_Dif"', html)
        self.assertIn('masonry-grid--native', html)
