from django.test import TestCase, Client
from django.urls import reverse
from core.models import Usuario

class TestMisReservas(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create(
            nombre="Luis",
            correo="luis@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )
        session = self.client.session
        session["usuario_id"] = self.user.id_usuario
        session.save()

    def test_mis_reservas_vacio(self):
        response = self.client.get(reverse("mis_reservas"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "reservas")
