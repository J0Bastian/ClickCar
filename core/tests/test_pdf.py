from django.test import TestCase, Client
from django.urls import reverse
from core.models.usuarios import Usuario
from core.models.vehiculo import Vehiculo
from core.models.reserva import Reserva

class TestPDF(TestCase):

    def setUp(self):
        self.client = Client()

        self.user = Usuario.objects.create(
            nombre="Pedro",
            correo="pedro@example.com",
            contrasena="123",
            nombre_rol="cliente"
        )

        self.vehicle = Vehiculo.objects.create(
            marca="Toyota",
            modelo="Corolla",
            precio_dia=150000,
            combustible="Gasolina",
            asientos="5",
        )

        self.reserva = Reserva.objects.create(
            usuario=self.user,
            auto=self.vehicle,
            fecha_inicio="2025-01-01",
            fecha_fin="2025-01-02",
            valor_total=150000
        )

        session = self.client.session
        session["usuario_id"] = self.user.id_usuario
        session.save()

    def test_descargar_pdf(self):
        response = self.client.get(reverse("pdf_reserva", args=[self.reserva.id_reserva]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response["Content-Type"])
