import re
from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse

from MainApp.models import Problem, ProblemProgress, TypeTag, Bundle
from UsersApp.models import User


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

    def test_training_picker_posts_directly_not_through_search(self):
        """T4/S4: the picker chooses a problem directly on Training."""
        _make_problem("Randomly pickable problem")
        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("one problem at a time", content)
        # The picker is a CSRF-protected POST on this route, never a link
        # into Search.
        self.assertIn('name="action" value="pick"', content)
        self.assertIn("csrfmiddlewaretoken", content)
        # No Search routing inside the picker itself (the navbar is shared).
        picker_section_start = content.index(
            'aria-labelledby="ss-training-practice-title"')
        picker_section_end = content.index("</section>", picker_section_start)
        picker_section = content[picker_section_start:picker_section_end]
        self.assertNotIn(f'href="{reverse("Search")}"', picker_section)
        # Truthful presentation: session-only state, never profile history.
        self.assertIn("session", content)
        self.assertIn("profile history", content)
        self.assertIn("not track", content)


class TrainingRandomPickerTests(TestCase):
    """T4/S4: random Problem picker with session-scoped pending status."""

    @staticmethod
    def _stable_content(response):
        # The CSRF token rotates on every render; it is not part of the
        # pick state being compared.
        return re.sub(r'(csrfmiddlewaretoken" value=")[^"]+',
                      r"\1TOKEN", response.content.decode())

    def _pick(self, follow=False):
        return self.client.post(reverse("Training"), {"action": "pick"},
                                follow=follow)

    def test_pick_redirects_and_marks_random_pending_problem(self):
        problem = _make_problem("Randomly pickable problem")

        response = self.client.post(reverse("Training"), {"action": "pick"},
                                    follow=True)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(problem.title, content)
        self.assertIn("pending", content)
        self.assertIn("csrfmiddlewaretoken", content)

    def test_pick_page_is_stable_across_gets_while_pending(self):
        _make_problem("Stable problem")

        self._pick(follow=True)

        first = self._stable_content(self.client.get(reverse("Training")))
        second = self._stable_content(self.client.get(reverse("Training")))
        self.assertIn("pending", first)
        self.assertEqual(first, second)

    def test_solved_clears_pending_and_marks_session_state(self):
        problem = _make_problem("Solved problem")
        self._pick(follow=True)

        response = self.client.post(reverse("Training"),
                                    {"action": "solved"}, follow=True)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("You marked", content)
        self.assertIn("solved", content)
        self.assertIn(problem.title, content)
        self.assertEqual(self._stable_content(self.client.get(
            reverse("Training"))), self._stable_content(response))
        self.assertIn('name="action" value="pick"', content)

    def test_give_up_clears_pending_and_marks_session_state(self):
        problem = _make_problem("Given-up problem")
        self._pick(follow=True)

        response = self.client.post(reverse("Training"),
                                    {"action": "give_up"}, follow=True)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("You gave up", content)
        self.assertIn(problem.title, content)
        self.assertEqual(self._stable_content(self.client.get(
            reverse("Training"))), self._stable_content(response))

    def test_pick_after_solved_starts_a_new_pending_problem(self):
        problem = _make_problem("Available problem")
        self._pick(follow=True)
        self.client.post(reverse("Training"), {"action": "solved"})

        response = self._pick(follow=True)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(problem.title, content)
        self.assertIn("pending", content)
        self.assertIn('name="action" value="solved"', content)

    def test_pick_with_empty_catalogue_leaves_session_unchanged(self):
        response = self._pick(follow=True)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("No problems available", content)
        self.assertNotIn("Current pick:", content)

    def test_get_picker_with_empty_catalogue_is_truthful(self):
        # Existing bundle list keeps rendering even with no problems.
        bundle = Bundle(title="Lonely bundle", slug="lonely-bundle",
                        embedding=list(EMBEDDING))
        Bundle.objects.bulk_create([bundle])

        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("No problems available", content)
        self.assertIn("Lonely bundle", content)

    def test_get_does_not_pick_and_unknown_action_is_ignored(self):
        _make_problem("Unpicked problem")

        response = self.client.get(
            reverse("Training") + "?action=pick", follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Current pick:", response.content.decode())

        self.client.post(reverse("Training"), {"action": "banana"})
        response = self.client.post(reverse("Training"),
                                    {"action": "solved"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Current pick:", response.content.decode())

    def test_pick_does_not_replace_a_pending_problem(self):
        pending = _make_problem("Keep this pending problem")
        replacement = _make_problem("Do not replace the pending problem")

        with patch("Training.views.random.choice",
                   side_effect=[pending.pk, replacement.pk]) as choose:
            first = self.client.post(reverse("Training"),
                                     {"action": "pick"}, follow=True)
            second = self.client.post(reverse("Training"),
                                      {"action": "pick"}, follow=True)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertIn(pending.title, second.content.decode())
        self.assertNotIn(replacement.title, second.content.decode())
        self.assertNotIn('name="action" value="pick"', second.content.decode())

    def test_anonymous_pending_pick_is_not_inherited_after_login(self):
        problem = _make_problem("Anonymous session problem")
        self.client.post(reverse("Training"), {"action": "pick"})

        user = User.objects.create_user(
            email="picker@example.com", username="picker", password="secret")
        self.client.force_login(user)
        response = self.client.get(reverse("Training"))

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertNotIn(problem.title, content)
        self.assertNotIn("Current pick:", content)
        self.assertIn("Get a random problem", content)


class TrainingLearningProgressTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="learning-progress@example.com",
            username="learning-progress",
            password="sturdy-Pass9!",
        )
        self.problem = _make_problem("Persisted training problem")

    def test_authenticated_outcome_persists_in_a_new_session(self):
        self.client.force_login(self.user)
        with patch("Training.views.random.choice", return_value=self.problem.pk):
            self.client.post(reverse("Training"), {"action": "pick"})
        self.client.post(reverse("Training"), {"action": "solved"})

        new_session = Client()
        new_session.force_login(self.user)
        response = new_session.get(reverse("UserInterface_problems", args=[self.user.username]))

        progress = ProblemProgress.objects.filter(user=self.user, problem=self.problem).first()
        self.assertIsNotNone(progress, "authenticated outcomes must persist beyond the training session")
        self.assertEqual(progress.status, "solved")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Persisted training problem")

    def test_retries_are_retained_and_progress_tracks_the_latest_exact_attempt(self):
        from MainApp.models import ProblemAttempt, ProblemProgress

        self.client.force_login(self.user)
        with patch("Training.views.random.choice", return_value=self.problem.pk):
            self.client.post(reverse("Training"), {"action": "pick"})
            self.client.post(reverse("Training"), {"action": "solved"})
            self.client.post(reverse("Training"), {"action": "pick"})
            self.client.post(reverse("Training"), {"action": "give_up"})

        attempts = list(
            ProblemAttempt.objects.filter(user=self.user, problem=self.problem).order_by("pk")
        )
        self.assertEqual([attempt.outcome for attempt in attempts], ["solved", "given_up"])
        self.assertEqual(
            ProblemProgress.objects.get(user=self.user, problem=self.problem).status,
            attempts[-1].outcome,
        )


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


class LearningDataTrainingFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="learner@example.com", username="learner", password="secret"
        )

    def _pick(self, client, problem, follow=True):
        with patch("Training.views.random.choice", return_value=problem.pk):
            return client.post(reverse("Training"), {"action": "pick"}, follow=follow)

    def test_authenticated_outcomes_persist_and_are_visible_only_to_the_owner(self):
        from MainApp.models import ProblemAttempt, ProblemProgress

        problem = _make_problem("Private progress problem")
        owner = self.client
        owner.force_login(self.user)
        self._pick(owner, problem)
        self.assertEqual(
            ProblemAttempt.objects.get(user=self.user, problem=problem).outcome,
            ProblemAttempt.Outcome.PENDING,
        )

        owner.post(reverse("Training"), {"action": "solved"})
        self.assertEqual(
            ProblemProgress.objects.get(user=self.user, problem=problem).status,
            ProblemProgress.Status.SOLVED,
        )
        self.assertEqual(
            ProblemAttempt.objects.get(user=self.user, problem=problem).outcome,
            ProblemAttempt.Outcome.SOLVED,
        )

        # A new authenticated session reads the durable profile record.
        from django.test import Client

        new_session = Client()
        new_session.force_login(self.user)
        owner_profile = new_session.get(
            reverse("UserInterface_problems", args=[self.user.username])
        )
        self.assertEqual(owner_profile.status_code, 200)
        self.assertContains(owner_profile, 'data-problem-status="solved"')

        public_profile = Client().get(
            reverse("UserInterface_problems", args=[self.user.username])
        )
        self.assertEqual(public_profile.status_code, 200)
        self.assertNotContains(public_profile, 'data-problem-status="solved"')
        self.assertIsNone(public_profile.context.get("problem_progress"))

    def test_retries_create_distinct_attempts_and_update_latest_progress(self):
        from MainApp.models import ProblemAttempt, ProblemProgress

        problem = _make_problem("Retryable problem")
        self.client.force_login(self.user)
        self._pick(self.client, problem)
        self.client.post(reverse("Training"), {"action": "solved"})
        self._pick(self.client, problem)
        self.client.post(reverse("Training"), {"action": "give_up"})

        self.assertEqual(
            list(ProblemAttempt.objects.filter(user=self.user, problem=problem).values_list(
                "outcome", flat=True
            )),
            [ProblemAttempt.Outcome.SOLVED, ProblemAttempt.Outcome.GIVEN_UP],
        )
        self.assertEqual(
            ProblemProgress.objects.get(user=self.user, problem=problem).status,
            ProblemProgress.Status.GIVEN_UP,
        )

    def test_owner_profile_shows_not_started_fallback_without_a_progress_row(self):
        problem = _make_problem("Not started problem")
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("UserInterface_problems", args=[self.user.username])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No started problems yet")
        self.assertNotContains(response, f'data-problem-status="not-started"')

    def test_training_pick_displays_top_two_tags_per_axis_in_weight_order(self):
        from MainApp.models import AreaTag, ProblemAreaWeight

        problem = _make_problem("Weighted problem")
        algebra = AreaTag.objects.create(kind="mathematical", name="Algebra")
        number_theory = AreaTag.objects.create(kind="mathematical", name="Number theory")
        geometry = AreaTag.objects.create(kind="mathematical", name="Geometry")
        proof = AreaTag.objects.create(kind="cognitive", name="Proof")
        visualization = AreaTag.objects.create(kind="cognitive", name="Visualization")
        for area, weight in (
            (algebra, "0.5000"),
            (number_theory, "0.3000"),
            (geometry, "0.2000"),
            (proof, "0.7000"),
            (visualization, "0.3000"),
        ):
            ProblemAreaWeight.objects.create(problem=problem, area=area, weight=weight)

        response = self._pick(self.client, problem)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertLess(html.index("Algebra"), html.index("Number theory"))
        self.assertLess(html.index("Proof"), html.index("Visualization"))
        self.assertNotIn("Geometry", html)
        for tag_name in ("Algebra", "Number theory", "Proof", "Visualization"):
            self.assertIn(f'<span class="badge ss-tag">{tag_name}</span>', html)
        area_markup = html.split('<div class="ss-problem-area-tags"', 1)[1].split(
            "</section>", 1
        )[0]
        self.assertNotIn("%", area_markup)
        self.assertNotIn("0.5000", area_markup)
        self.assertNotIn("0.7000", area_markup)

    def test_training_pick_shows_unclassified_for_empty_axes(self):
        problem = _make_problem("Problem with no area tags")

        response = self._pick(self.client, problem)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode().count("Unclassified"), 2)
