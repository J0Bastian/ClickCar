from django.test import TestCase
from django.urls import reverse
from datetime import date, timedelta
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva


class TestCancelarReserva(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create(
            nombre="Pedro",
            correo="pedro@test.com",
            contrasena="123"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Mazda",
            modelo="CX5",
            precio_dia=200000,
            color="Rojo"
        )

        self.reserva = Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio=date.today() + timedelta(days=5),
            fecha_fin=date.today() + timedelta(days=7),
            valor_total=400000
        )

        self.client.session["usuario_id"] = self.user.id_usuario
        self.client.session.save()

    def test_cancelar_reserva(self):
        r = self.client.get(reverse("cancelar_reserva", args=[self.reserva.id_reserva]))
        self.assertEqual(r.status_code, 302)
