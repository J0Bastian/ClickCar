from django.test import TestCase, Client
from django.urls import reverse

class TestConfirmarReservaSinSession(TestCase):

    def test_confirmar_reserva_sin_datos(self):
        client = Client()
        response = client.get(reverse("confirmar_reserva"))
        self.assertEqual(response.status_code, 302)
