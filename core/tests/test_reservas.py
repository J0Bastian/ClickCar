from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva


class TestReservas(TestCase):

    def setUp(self):
        self.client = Client()
        self.usuario = Usuario.objects.create(
            nombre="Bastian",
            correo="b@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )
        self.auto = Vehiculo.objects.create(
            marca="Mazda", modelo="CX-5", precio_dia=200000
        )

        session = self.client.session
        session["usuario_id"] = self.usuario.id_usuario
        session.save()

    def test_crear_reserva_valida(self):
        response = self.client.post(reverse("reserva", args=[self.auto.id_vehiculo]), {
            "fecha_inicio": "2025-10-10",
            "fecha_fin": "2025-10-12"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("confirmar_reserva"))

    def test_conflicto_fechas(self):
        Reserva.objects.create(
            usuario=self.usuario,
            auto=self.auto,
            fecha_inicio="2025-10-10",
            fecha_fin="2025-10-12",
            valor_total=200000
        )

        response = self.client.post(reverse("reserva", args=[self.auto.id_vehiculo]), {
            "fecha_inicio": "2025-10-11",
            "fecha_fin": "2025-10-13"
        })
        self.assertEqual(response.status_code, 302)

    def test_confirmar_reserva(self):
        session = self.client.session
        session["datos_reserva"] = {
            "vehiculo_id": self.auto.id_vehiculo,
            "fecha_inicio": "2025-10-10",
            "fecha_fin": "2025-10-12",
            "valor_total": 400000,
        }
        session.save()

        response = self.client.post(reverse("confirmar_reserva"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("home"))
