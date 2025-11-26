from django.test import TestCase, Client

class TestRootURL(TestCase):

    def test_root_status(self):
        client = Client()
        response = client.get("/")
        self.assertIn(response.status_code, [200, 302])
