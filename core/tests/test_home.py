from django.test import TestCase, Client
from django.urls import reverse
from core.models.vehiculo import Vehiculo


class TestHome(TestCase):

    def setUp(self):
        self.client = Client()
        Vehiculo.objects.create(marca="Nissan", modelo="Versa", precio_dia=95000)

    def test_mostrar_home(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Nissan")
