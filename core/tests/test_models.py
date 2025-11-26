from django.test import TestCase
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva

class TestModels(TestCase):

    def test_usuario_str(self):
        u = Usuario.objects.create(
            nombre="Juan",
            correo="juan@example.com",
            contrasena="123",
            telefono="12345",
            nombre_rol="cliente"
        )
        self.assertEqual(str(u), "Juan (cliente)")

    def test_vehiculo_str(self):
        v = Vehiculo.objects.create(
            marca="Toyota",
            modelo="Corolla",
            categoria="Sedán",
            anio=2020,
            precio_dia=100000,
            descripcion="Auto económico",
            foto_url="img.jpg",
            combustible="Gasolina",
            asientos="5",
            color="Rojo"
        )
        self.assertEqual(str(v), "Toyota Corolla")

    def test_reserva_str(self):
        u = Usuario.objects.create(
            nombre="Ana",
            correo="ana@example.com",
            contrasena="333",
            nombre_rol="cliente"
        )
        v = Vehiculo.objects.create(
            marca="Mazda",
            modelo="3",
            precio_dia=120000,
            combustible="Gasolina",
            asientos="5"
        )
        r = Reserva.objects.create(
            usuario=u,
            auto=v,
            fecha_inicio="2025-01-01",
            fecha_fin="2025-01-02",
            estado="pendiente",
            valor_total=240000
        )
        self.assertIn("Reserva", str(r))
