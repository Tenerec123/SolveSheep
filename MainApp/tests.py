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
