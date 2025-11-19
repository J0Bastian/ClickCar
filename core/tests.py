from django.test import TestCase, Client
from django.urls import reverse

class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_status_code(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
