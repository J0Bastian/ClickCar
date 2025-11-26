from django.test import TestCase, Client
from django.urls import reverse
from core.models import Usuario, Vehiculo, Reserva

class TestDetalleReserva(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = Usuario.objects.create(
            nombre="Ana",
            correo="ana@example.com",
            contrasena="123",
            nombre_rol="cliente",
        )
        self.vehicle = Vehiculo.objects.create(
            marca="Mazda",
            modelo="CX5",
            precio_dia=180000,
            combustible="Gasolina",
            asientos="5"
        )
        self.reserva = Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio="2025-01-01",
            fecha_fin="2025-01-02",
            valor_total=180000
        )

    def test_detalle_reserva(self):
        response = self.client.get(reverse("detalle_reserva", args=[self.reserva.id_reserva]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Reserva")
    def test_reserva_con_conflicto(self):
        Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio="2025-02-01",
            fecha_fin="2025-02-10",
            valor_total=300000
        )

        response = self.client.post(reverse("reserva", args=[self.vehicle.id_vehiculo]), {
            "fecha_inicio": "2025-02-05",
            "fecha_fin": "2025-02-08"
        })

        self.assertEqual(response.status_code, 302)
        self.assertNotIn("datos_reserva", self.client.session)
