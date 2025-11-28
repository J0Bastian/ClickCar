from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario


class TestPerfiles(TestCase):

    def setUp(self):
        self.admin = Usuario.objects.create(
            nombre="Admin",
            correo="admin@test.com",
            contrasena="123",
            nombre_rol="admin"
        )

        self.user = Usuario.objects.create(
            nombre="Cliente",
            correo="cliente@test.com",
            contrasena="123"
        )

        self.client.session["usuario_rol"] = "admin"
        self.client.session.save()

def visualizar_perfiles(request):
    if request.session.get("usuario_rol") != "admin":
        return redirect("login")

    return render(request, "core/visualizar_perfiles.html", {
        "usuarios": Usuario.objects.all(),
        "reservas": Reserva.objects.all(),
        "vehiculos": Vehiculo.objects.all()
    })
    def test_perfil_usuario(self):
        r = self.client.get(reverse("perfil_usuario", args=[self.user.id_usuario]))
        self.assertEqual(r.status_code, 200)
