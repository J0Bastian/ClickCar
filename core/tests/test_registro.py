from django.test import TestCase
from django.urls import reverse


class TestRegistro(TestCase):

    def test_registro_envia_codigo(self):
        r = self.client.post(reverse("registro"), {
            "nombre": "Luis",
            "correo": "luis@test.com",
            "contrasena": "123",
            "telefono": "3001231234"
        })
        self.assertEqual(r.status_code, 302)
        self.assertIn("registro_temp", self.client.session)
