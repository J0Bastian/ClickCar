from django.test import TestCase
from django.urls import reverse
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva
from datetime import date


class TestDetalleReserva(TestCase):

    def setUp(self):
        self.user = Usuario.objects.create(
            nombre="Carlos",
            correo="carlos@test.com",
            contrasena="123"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Renault",
            modelo="Duster",
            precio_dia=120000,
            color="Gris"
        )

        self.reserva = Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio=date.today(),
            fecha_fin=date.today(),
            valor_total=120000
        )

        self.client.session["usuario_id"] = self.user.id_usuario
        self.client.session.save()

def ver_detalle_reserva(request, id_reserva):
    reserva = get_object_or_404(Reserva, id_reserva=id_reserva)

    usuario_id = request.session.get("usuario_id") or request.session.get("id_usuario")

    # Solo admin o dueño
    if request.session.get("usuario_rol") != "admin":
        if reserva.usuario.id_usuario != usuario_id:
            return redirect("mis_reservas")

    return render(request, "core/detalle_reserva.html", {"reserva": reserva})