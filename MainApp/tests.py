from django.test import TestCase


class ThemeFoundationTests(TestCase):
    """T2/S1: shared theme tokens, early no-flash application, and the
    accessible persistent toggle wired into the shared base template."""

    def test_public_page_wires_theme_tokens_toggle_and_script(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        # Shared theme stylesheet is linked from the base shell.
        self.assertIn('css/workshop.css', html)

        # Early inline script applies both theme attributes before any
        # body markup renders, so first paint never flashes the wrong theme.
        head = html[:html.index('<body')]
        self.assertIn("data-bs-theme", head)
        self.assertIn("data-theme", head)
        self.assertIn("prefers-color-scheme", head)
        self.assertIn('localStorage', head)

        # Toggle is a native keyboard-operable button with an accurate
        # accessible name and pressed state.
        marker = html.index('data-theme-toggle')
        self.assertIn('<button', html[:marker])
        self.assertIn('type="button"', html[marker - 200:marker])
        self.assertIn('aria-pressed', html)
        self.assertIn('aria-label', html)

        # Theme script is loaded so persistence and OS-following work.
        self.assertIn('js/theme.js', html)


class RemovedEndpointsTests(TestCase):
    def test_json_import_route_removed(self):
        response = self.client.get("/json/")
        self.assertEqual(response.status_code, 404)


class LearningDataSchemaTests(TestCase):
    """T1 schema contracts for independently normalized learning data."""

    @classmethod
    def setUpTestData(cls):
        from unittest.mock import patch

        from django.contrib.auth import get_user_model
        from MainApp.models import Problem

        cls.embedding_patch = patch("MainApp.models.get_embedding_model")
        embedding_model = cls.embedding_patch.start()
        embedding_model.return_value.encode.return_value = type(
            "Embedding", (), {"tolist": lambda self: [0.0] * 384}
        )()
        cls.addClassCleanup(cls.embedding_patch.stop)

        cls.user = get_user_model().objects.create_user(
            username="learning-user", email="learning@example.com", password="test-password"
        )
        cls.other_user = get_user_model().objects.create_user(
            username="other-learning-user", email="other-learning@example.com", password="test-password"
        )
        cls.problem = Problem.objects.create(title="Learning data problem")
        cls.other_problem = Problem.objects.create(title="Another learning data problem")

    def _create_area(self, name, kind):
        from MainApp.models import AreaTag

        return AreaTag.objects.create(name=name, kind=kind)

    def _area_formset(self, entries):
        from django.forms import inlineformset_factory
        from MainApp.admin import ProblemAreaWeightInlineFormSet
        from MainApp.models import Problem, ProblemAreaWeight

        formset_class = inlineformset_factory(
            Problem,
            ProblemAreaWeight,
            formset=ProblemAreaWeightInlineFormSet,
            fields=("area", "weight"),
            extra=0,
        )
        data = {
            "weights-TOTAL_FORMS": str(len(entries)),
            "weights-INITIAL_FORMS": "0",
            "weights-MIN_NUM_FORMS": "0",
            "weights-MAX_NUM_FORMS": "1000",
        }
        for index, (area, weight) in enumerate(entries):
            data[f"weights-{index}-area"] = str(area.pk)
            data[f"weights-{index}-weight"] = str(weight)
        return formset_class(data=data, instance=self.problem, prefix="weights")

    def test_populated_area_axis_requires_positive_shares_summing_to_one(self):
        math_one = self._create_area("Algebra", "mathematical")
        math_two = self._create_area("Number theory", "mathematical")
        self.assertFalse(self._area_formset([(math_one, "0.6"), (math_two, "0.3")]).is_valid())
        self.assertFalse(self._area_formset([(math_one, "0"), (math_two, "1")]).is_valid())
        self.assertTrue(self._area_formset([(math_one, "0.6"), (math_two, "0.4")]).is_valid())

    def test_cognitive_and_math_distributions_are_normalized_independently(self):
        math = self._create_area("Combinatorics", "mathematical")
        cognitive = self._create_area("Proof construction", "cognitive")
        self.assertTrue(self._area_formset([(math, "1"), (cognitive, "1")]).is_valid())

    def test_progress_and_attempts_are_per_user_and_retries_are_retained(self):
        from MainApp.models import ProblemAttempt, ProblemProgress

        expected = {"pending", "solved", "given_up"}
        self.assertEqual({value for value, _label in ProblemProgress.Status.choices}, expected)
        self.assertFalse(ProblemProgress.objects.filter(user=self.user, problem=self.problem).exists())
        ProblemProgress.objects.create(user=self.user, problem=self.problem, status="solved")
        ProblemAttempt.objects.create(user=self.user, problem=self.problem, outcome="solved")
        ProblemAttempt.objects.create(user=self.user, problem=self.problem, outcome="given_up")
        self.assertEqual(ProblemAttempt.objects.filter(user=self.user, problem=self.problem).count(), 2)
        self.assertFalse(ProblemProgress.objects.filter(user=self.other_user, problem=self.problem).exists())

    def test_area_rating_is_integer_and_unique_per_user_and_area(self):
        from django.db import IntegrityError, transaction
        from MainApp.models import AreaRating

        area = self._create_area("Geometry", "mathematical")
        rating_field = AreaRating._meta.get_field("rating")
        self.assertEqual(rating_field.get_internal_type(), "IntegerField")
        AreaRating.objects.create(user=self.user, area=area, rating=1475)
        with self.assertRaises(IntegrityError), transaction.atomic():
            AreaRating.objects.create(user=self.user, area=area, rating=1500)
        self.assertFalse(AreaRating.objects.filter(user=self.other_user).exists())

    def test_hints_are_ordered_and_order_uniqueness_is_problem_scoped(self):
        from django.db import IntegrityError, transaction
        from MainApp.models import ProblemHint

        first = ProblemHint.objects.create(problem=self.problem, position=1, text="Try a small case.")
        second = ProblemHint.objects.create(problem=self.problem, position=2, text="Look for an invariant.")
        other_first = ProblemHint.objects.create(problem=self.other_problem, position=1, text="Draw a diagram.")
        self.assertEqual(list(self.problem.hints.values_list("pk", flat=True)), [first.pk, second.pk])
        self.assertEqual(other_first.position, 1)
        with self.assertRaises(IntegrityError), transaction.atomic():
            ProblemHint.objects.create(problem=self.problem, position=1, text="Duplicate order.")

    def test_migration_only_adds_learning_data_models(self):
        from importlib import import_module

        migration_module = import_module("MainApp.migrations.0005_learning_data_models")
        operations = migration_module.Migration.operations
        self.assertTrue(operations)
        additive_operations = {"CreateModel", "AddField", "AddConstraint"}
        self.assertTrue(all(operation.__class__.__name__ in additive_operations for operation in operations))
