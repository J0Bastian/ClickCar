from django.test import TestCase, Client
from django.urls import reverse
from core.models import Usuario, Vehiculo, Reserva

class TestReservaLogica(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = Usuario.objects.create(
            nombre="Carlos",
            correo="carlos@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Mazda",
            modelo="3",
            precio_dia=120000,
            combustible="Gasolina",
            asientos="5"
        )

        session = self.client.session
        session["usuario_id"] = self.user.id_usuario
        session.save()

    def test_reserva_exitosa(self):
        response = self.client.post(reverse("reserva", args=[self.vehicle.id_vehiculo]), {
            "fecha_inicio": "2025-02-01",
            "fecha_fin": "2025-02-05"
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("datos_reserva", self.client.session)
