from django.test import TestCase


class RemovedEndpointsTests(TestCase):
    def test_json_import_route_removed(self):
        response = self.client.get("/json/")
        self.assertEqual(response.status_code, 404)
