from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo


class TestConfirmarReserva(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create(
            nombre="Ana",
            correo="ana@test.com",
            contrasena="123"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Kia",
            modelo="Rio",
            precio_dia=80000,
            color="Negro"
        )

        self.client.session["usuario_id"] = self.user.id_usuario
        self.client.session["datos_reserva"] = {
            "vehiculo_id": self.vehicle.id_auto,
            "fecha_inicio": "2025-01-01",
            "fecha_fin": "2025-01-02",
            "dias": 2,
            "valor_total": "160000"
        }
        self.client.session.save()

    def test_confirmar_reserva(self):
        r = self.client.post(reverse("confirmar_reserva"))
        self.assertEqual(r.status_code, 302)
