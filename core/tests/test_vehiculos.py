from django.test import TestCase, Client
from django.urls import reverse
from core.models.vehiculo import Vehiculo
from core.models.usuarios import Usuario


class TestVehiculos(TestCase):

    def setUp(self):
        self.client = Client()

        # Crear admin autenticado
        self.admin = Usuario.objects.create(
            nombre="Admin",
            correo="admin@example.com",
            contrasena="123",
            nombre_rol="admin"
        )

        session = self.client.session
        session["usuario_id"] = self.admin.id_usuario
        session["usuario_rol"] = "admin"
        session.save()

        # Vehículo de prueba
        self.auto = Vehiculo.objects.create(
            marca="Mazda",
            modelo="3",
            precio_dia=120000,
            combustible="Gasolina",
            asientos="5",
            color="Rojo"
        )

    # -----------------------------
    # LISTA
    # -----------------------------
    def test_lista_vehiculos_status(self):
        response = self.client.get(reverse("lista_vehiculos"))
        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # AGREGAR
    # -----------------------------
    def test_agregar_vehiculo_sin_campos(self):
        response = self.client.post(reverse("agregar_vehiculo"), {})
        self.assertEqual(response.status_code, 200)

    def test_agregar_vehiculo_sin_combustible(self):
        response = self.client.post(reverse("agregar_vehiculo"), {
            "marca": "Kia",
            "modelo": "Rio",
            "precio_dia": 150000,
            "asientos": "5",
            "color": "Azul"
        })
        self.assertEqual(response.status_code, 200)

    # -----------------------------
    # ELIMINAR
    # -----------------------------
    def test_eliminar_vehiculo_ok(self):
        response = self.client.get(reverse("eliminar_vehiculo",
                                           args=[self.auto.id_vehiculo]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Vehiculo.objects.filter(id_vehiculo=self.auto.id_vehiculo).exists())

    def test_eliminar_vehiculo_inexistente(self):
        response = self.client.get(reverse("eliminar_vehiculo", args=[9999]))
        self.assertIn(response.status_code, [404, 302])

    def test_eliminar_vehiculo_sin_permiso(self):
        session = self.client.session
        session["usuario_rol"] = "cliente"
        session.save()

        response = self.client.get(reverse("eliminar_vehiculo",
                                           args=[self.auto.id_vehiculo]))
        self.assertIn(response.status_code, [302, 403])
