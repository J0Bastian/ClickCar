from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario


class TestPanelAdmin(TestCase):

    def setUp(self):
        self.admin = Usuario.objects.create(
            nombre="Admin",
            correo="admin@test.com",
            contrasena="123",
            nombre_rol="admin"
        )
        self.client.session["usuario_rol"] = "admin"
        self.client.session.save()

def panel_reservas(request):
    if request.session.get("usuario_rol") != "admin":
        return redirect("login")

    return render(request, "core/panel_reservas.html", {
        "reservas": Reserva.objects.all()
    })
