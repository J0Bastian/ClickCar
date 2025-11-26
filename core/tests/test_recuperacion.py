from django.test import TestCase, Client
from django.urls import reverse
from core.models.usuarios import Usuario


class TestRecuperacion(TestCase):

    def setUp(self):
        self.client = Client()
        Usuario.objects.create(
            nombre="Bastian",
            correo="test@example.com",
            contrasena="12345",
            nombre_rol="cliente"
        )

    def test_enviar_codigo_recuperacion(self):
        response = self.client.post(reverse("olvide_password"), {
            "correo": "test@example.com"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("verificar_codigo_reset"))

    def test_verificar_codigo_reset_incorrecto(self):
        session = self.client.session
        session["reset"] = {"codigo": 555555}
        session.save()

        response = self.client.post(reverse("verificar_codigo_reset"), {
            "codigo": "000000"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("verificar_codigo_reset"))

    def test_cambiar_contrasena(self):
        session = self.client.session
        session["reset"] = {"correo": "test@example.com"}
        session.save()

        response = self.client.post(reverse("nueva_contrasena"), {
            "contrasena": "new123"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))
