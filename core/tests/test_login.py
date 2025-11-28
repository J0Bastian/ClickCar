from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario


class TestLogin(TestCase):

    def setUp(self):
        Usuario.objects.create(
            nombre="Test",
            correo="test@test.com",
            contrasena="123"
        )

    def test_login_correcto(self):
        r = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "123"
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn("usuario_id", self.client.session)

    def test_login_incorrecto(self):
        r = self.client.post(reverse("login"), {
            "username": "test@test.com",
            "password": "xxx"
        })
        self.assertEqual(r.status_code, 200)
