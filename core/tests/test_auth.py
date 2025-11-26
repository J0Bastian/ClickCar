from django.test import TestCase, Client
from django.urls import reverse
from core.models.usuarios import Usuario


class TestAuth(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(
            nombre="Bastian",
            correo="test@example.com",
            contrasena="12345",
            telefono="3001234567",
            nombre_rol="cliente"
        )

    def test_login_correcto(self):
        response = self.client.post(reverse("login"), {
            "username": "test@example.com",
            "password": "12345"
        })
        # Debe redirigir a products
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("products"))

    def test_login_incorrecto(self):
        response = self.client.post(reverse("login"), {
            "username": "test@example.com",
            "password": "mal"
        })
        self.assertContains(response, "Correo o contraseña incorrectos.")
