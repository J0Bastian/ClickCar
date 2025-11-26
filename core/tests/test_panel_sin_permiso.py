from django.test import TestCase, Client
from core.models import Usuario
from django.urls import reverse

class TestPanelReservasSinPermiso(TestCase):

    def setUp(self):
        self.client = Client()
        u = Usuario.objects.create(
            nombre="Luis",
            correo="l@x.com",
            contrasena="123",
            nombre_rol="cliente"
        )
        session = self.client.session
        session["usuario_id"] = u.id_usuario
        session["usuario_rol"] = "cliente"
        session.save()

    def test_panel_reservas_sin_permiso(self):
        response = self.client.get(reverse("panel_reservas"))
        self.assertEqual(response.status_code, 302)
