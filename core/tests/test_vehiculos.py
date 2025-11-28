from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo


class TestVehiculos(TestCase):

    def setUp(self):
        self.admin = Usuario.objects.create(
            nombre="Admin",
            correo="admin@test.com",
            contrasena="123",
            nombre_rol="admin"
        )
        self.client.session["usuario_rol"] = "admin"
        self.client.session.save()

        self.vehicle = Vehiculo.objects.create(
            marca="Ford",
            modelo="Fiesta",
            precio_dia=80000,
            color="Rojo"
        )

def test_agregar_vehiculo_sin_campos(self):
    r = self.client.post(reverse("agregar_vehiculo"), {}, follow=True)
    self.assertEqual(r.status_code, 200)


    def test_eliminar_vehiculo(self):
        r = self.client.get(reverse("eliminar_vehiculo", args=[self.vehicle.id_auto]))
        self.assertEqual(r.status_code, 302)
