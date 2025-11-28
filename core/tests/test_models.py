from django.test import TestCase
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva
from datetime import date
from decimal import Decimal


class TestModels(TestCase):

    def test_usuario_str(self):
        u = Usuario.objects.create(
            nombre="Juan",
            correo="juan@test.com",
            contrasena="123"
        )
        self.assertEqual(str(u), "Juan")

    def test_vehiculo_str(self):
        v = Vehiculo.objects.create(
            marca="Toyota",
            modelo="Corolla",
            precio_dia=100000,
            color="Rojo"
        )
        self.assertEqual(str(v), "Toyota Corolla")

    def test_reserva_str(self):
        u = Usuario.objects.create(
            nombre="Karla",
            correo="karla@test.com",
            contrasena="123"
        )
        v = Vehiculo.objects.create(
            marca="Mazda",
            modelo="3",
            precio_dia=150000,
            color="Negro"
        )
        r = Reserva.objects.create(
            usuario=u,
            auto=v,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            valor_total=Decimal("150000"),
            estado="confirmada"
        )
        self.assertIn("Reserva", str(r))
