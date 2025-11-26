from django.test import TestCase, Client
from django.urls import reverse
from core.models import Usuario

class TestEditarUsuario(TestCase):

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

        self.user = Usuario.objects.create(
            nombre="Luis",
            correo="luis@example.com",
            contrasena="111",
            nombre_rol="cliente"
        )

    def test_editar_usuario(self):
        response = self.client.post(reverse("editar_usuario", args=[self.user.id_usuario]), {
            "nombre": "Luis Editado",
            "correo": "nuevo@example.com",
            "telefono": "999",
            "rol": "cliente",   # ← CORRECTO
            "activo": "on"
        })

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nombre, "Luis Editado")
