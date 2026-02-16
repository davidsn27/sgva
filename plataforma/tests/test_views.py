from django.test import Client, TestCase
from django.urls import reverse

from plataforma.models import Aprendiz, Empresa


class ViewsTestCase(TestCase):
    """Test cases para las vistas de plataforma"""

    def setUp(self):
        """Configurar cliente de prueba y datos"""
        self.client = Client()
        self.aprendiz = Aprendiz.objects.create(
            nombres="Carlos",
            apellidos="López",
            email="carlos@example.com",
            estado="DISPONIBLE",
        )
        self.emprIsa = Empresa.objects.create(
            nombre="DeSPONIBLE",
        )
        self.empresa = Empresa.objects.create(
            nombre="DevCorp", nit="111222333", cupos=2
        )

    def test_landing_page_loads(self):
        """Verificar que la página de inicio carga correctamente"""
        response = self.client.get(reverse("landing"))
        self.assertEqual(response.status_code, 200)

    def test_aprendices_list_view(self):
        """Verificar que la lista de aprendices carga"""
        response = self.client.get(reverse("aprendices"))
        self.assertIn(self.aprendiz, response.context["aprendices"])

    def test_empresas_list_view(self):
        self.assertIn(self.empresa, response.context["empresas"])
