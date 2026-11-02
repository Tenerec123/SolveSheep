from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from MainApp.models import AreaTag, DifTag, Problem, ProblemAreaWeight, TypeTag
from UsersApp.models import User


class AreaTagDisplayTests(TestCase):
    def setUp(self):
        self.type_tag = TypeTag.objects.create(name="Existing topic", color="#123456")
        self.owner = User.objects.create_user(
            email="area-display@example.com",
            username="area-display-owner",
            password="sturdy-Pass9!",
        )
        self.problem = Problem(
            title="Weighted area display",
            slug="weighted-area-display",
            embedding=[0.1] * 384,
            author=self.owner,
            dif_tag=DifTag.objects.create(name=1),
        )
        self.problem.save()
        self.problem.type_tags.add(self.type_tag)

        area_weights = (
            ("cognitive", "Cognitive highest", "0.5000"),
            ("cognitive", "Cognitive second", "0.3000"),
            ("cognitive", "Cognitive third", "0.2000"),
            ("mathematical", "Math highest", "0.4500"),
            ("mathematical", "Math second", "0.3500"),
            ("mathematical", "Math third", "0.2000"),
        )
        for kind, name, weight in area_weights:
            area = AreaTag.objects.create(kind=kind, name=name)
            ProblemAreaWeight.objects.create(
                problem=self.problem,
                area=area,
                weight=Decimal(weight),
            )

    def test_problem_cards_and_detail_show_only_top_two_tags_per_axis(self):
        search_url = (
            f"{reverse('Search')}?Dif=0&Type=0&Text=&Start_Dif=0&End_Dif=0&Range=false"
        )
        responses = (
            self.client.get(reverse("Main")),
            self.client.get(search_url),
            self.client.get(
                reverse("UserInterface_problems", args=[self.owner.username])
            ),
            self.client.get(reverse("Problem", args=[self.problem.slug])),
        )

        for response in responses:
            self.assertEqual(response.status_code, 200)
            html = response.content.decode()
            self.assertIn("Existing topic", html)
            self.assertIn("Cognitive highest", html)
            self.assertIn("Cognitive second", html)
            self.assertNotIn("Cognitive third", html)
            self.assertIn("Math highest", html)
            self.assertIn("Math second", html)
            self.assertNotIn("Math third", html)

            cognitive_axis = html.split('data-area-axis="cognitive"', 1)[1].split("</div>", 1)[0]
            mathematical_axis = html.split('data-area-axis="mathematical"', 1)[1].split("</div>", 1)[0]
            self.assertLess(cognitive_axis.index("Cognitive highest"), cognitive_axis.index("Cognitive second"))
            self.assertLess(mathematical_axis.index("Math highest"), mathematical_axis.index("Math second"))
            self.assertNotIn("%", cognitive_axis + mathematical_axis)
            self.assertNotIn("0.5000", cognitive_axis)
            self.assertNotIn("0.4500", mathematical_axis)
