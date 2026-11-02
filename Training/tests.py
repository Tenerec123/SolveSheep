from django.test import TestCase
from django.urls import reverse

from MainApp.models import Problem, TypeTag, Bundle


# Fixed embedding value so creating problems never loads the sentence
# transformer (models only compute it when the field is empty).
EMBEDDING = [0.1] * 384


def _make_problem(title, tags=()):
    problem = Problem(title=title, embedding=list(EMBEDDING))
    problem.save()  # embedding already set; no transformer required
    problem.type_tags.set(tags)
    return problem


class RemovedEndpointsTests(TestCase):
    def test_ai_generation_route_removed(self):
        from django.urls.exceptions import NoReverseMatch
        with self.assertRaises(NoReverseMatch):
            reverse("Create_Problem")


class TrainingTagSetTests(TestCase):
    """T4/S4: tag-based virtual practice sets on the Training page."""

    def test_training_links_each_tagged_practice_set(self):
        tagged = TypeTag.objects.create(name="Geometry", color="#123456")
        empty = TypeTag.objects.create(name="Vacuous", color="#654321")
        _make_problem("Problem one", [tagged])
        _make_problem("Problem two", [tagged])

        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        search_url = reverse("Search")
        # Existing Search Type GET parameter, difficulties unrestricted.
        self.assertIn(f"{search_url}?Type={tagged.id}&Dif=0", content)
        # Only sets that actually have problems are offered.
        self.assertNotIn(f"Type={empty.id}", content)
        self.assertIn("Geometry", content)
        self.assertIn("2 problems", content)

    def test_training_lists_tagless_tag_skip_and_empty_state(self):
        tag = TypeTag.objects.create(name="Forgotten", color="#111111")

        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn(f"Type={tag.id}", content)
        self.assertIn("No practice sets yet", content)

    def test_training_one_problem_cta_routes_to_search(self):
        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("one problem at a time", content)
        self.assertIn(f'href="{reverse("Search")}"', content)
        # Truthful presentation: attempts are not persisted anywhere.
        self.assertIn("not stored", content)


class TrainingBundleListTests(TestCase):
    """T4/S4: the existing bundle list keeps rendering as before."""

    def test_training_still_lists_bundles(self):
        problem = _make_problem("Inside a bundle")
        bundle = Bundle(title="Warm bundle", slug="warm-bundle",
                        embedding=list(EMBEDDING))
        Bundle.objects.bulk_create([bundle])
        bundle.problems.set([problem])

        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Warm bundle", content)
        self.assertIn(reverse("Bundle", args=["warm-bundle"]), content)
