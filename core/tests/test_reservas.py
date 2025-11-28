from django.test import TestCase
from django.urls import reverse
from datetime import date
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva


class TestReservas(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create(
            nombre="Luis",
            correo="luis@test.com",
            contrasena="123"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Nissan",
            modelo="Versa",
            precio_dia=90000,
            color="Azul"
        )

        self.client.session["usuario_id"] = self.user.id_usuario
        self.client.session.save()

def test_crear_reserva_valida(self):
    url = reverse("reserva", args=[self.vehicle.id_auto])
    r = self.client.post(url, {
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-01-03",
    }, follow=True)
    self.assertIn("datos_reserva", self.client.session)


    def test_conflicto_de_fechas(self):
        Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio=date(2025, 1, 1),
            fecha_fin=date(2025, 1, 10),
            valor_total=100,
            estado="confirmada"
        )

        url = reverse("reserva", args=[self.vehicle.id_auto])
        r = self.client.post(url, {
            "fecha_inicio": "2025-01-05",
            "fecha_fin": "2025-01-07",
        })
        self.assertEqual(r.status_code, 302)
