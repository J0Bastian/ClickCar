from django.test import TestCase, Client
from django.urls import reverse

class TestProducts(TestCase):

    def setUp(self):
        self.client = Client()

    def test_products_sin_sesion(self):
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, 302)

    def test_products_sin_login(self):
        self.client.session.flush()  # Limpia sesión
        response = self.client.get(reverse("products"))
        self.assertEqual(response.status_code, 302)
