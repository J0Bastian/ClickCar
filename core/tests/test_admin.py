from django.test import TestCase, Client
from django.urls import reverse
from core.models.usuarios import Usuario


class TestAdmin(TestCase):

    def setUp(self):
        self.client = Client()
        admin = Usuario.objects.create(
            nombre="Admin",
            correo="admin@example.com",
            contrasena="123",
            nombre_rol="admin"
        )
        session = self.client.session
        session["usuario_id"] = admin.id_usuario
        session["usuario_rol"] = "admin"
        session.save()

    def test_visualizar_perfiles_admin(self):
        response = self.client.get(reverse("visualizar_perfiles"))
        self.assertEqual(response.status_code, 200)

   