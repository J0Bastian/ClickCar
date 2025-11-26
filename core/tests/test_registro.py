from django.test import TestCase, Client
from django.urls import reverse
from core.models.usuarios import Usuario


class TestRegistro(TestCase):

    def setUp(self):
        self.client = Client()

    def test_registro_usuario_nuevo(self):
        response = self.client.post(reverse("registro"), {
            "nombre": "Nuevo",
            "correo": "nuevo@example.com",
            "contrasena": "123",
            "telefono": "300"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("verificar_codigo"))

    def test_registro_correo_existente(self):
        Usuario.objects.create(
            nombre="Ana",
            correo="ana@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )
        response = self.client.post(reverse("registro"), {
            "nombre": "Test",
            "correo": "ana@example.com",
            "contrasena": "123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("registro"))

    def test_verificar_codigo_correcto(self):
        session = self.client.session
        session["registro_temp"] = {
            "nombre": "A",
            "correo": "a@example.com",
            "contrasena": "111",
            "telefono": "333",
            "codigo": 123456
        }
        session.save()

        response = self.client.post(reverse("verificar_codigo"), {
            "codigo": "123456"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def test_verificar_codigo_incorrecto(self):
        session = self.client.session
        session["registro_temp"] = {"codigo": 999999}
        session.save()

        response = self.client.post(reverse("verificar_codigo"), {
            "codigo": "111111"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("verificar_codigo"))
