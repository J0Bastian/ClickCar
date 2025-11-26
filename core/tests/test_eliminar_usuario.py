from django.test import TestCase, Client
from django.urls import reverse
from core.models import Usuario

class TestEliminarUsuario(TestCase):

    def setUp(self):
        self.client = Client()
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

    def test_eliminar_usuario(self):
        user = Usuario.objects.create(
            nombre="Carlos",
            correo="c@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )
        response = self.client.get(reverse("eliminar_usuario", args=[user.id_usuario]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Usuario.objects.filter(id_usuario=user.id_usuario).exists())
