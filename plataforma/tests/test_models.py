from django.test import TestCase

from plataforma.models import Aprendiz, Empresa, Postulacion


class AprendizModelTest(TestCase):
    """Test cases para el modelo Aprendiz"""

    def setUp(self):
        """Crear aprendiz de prueba"""
        self.aprendiz = Aprendiz.objects.create(
            nombre="Juan Pérez",
            correo="juan@example.com",
            telefono="3001234567",
            estado="DISPONIBLE",
        )

    def test_aprendiz_creation(self):
        """Verificar creación de aprendiz"""
        self.assertEqual(self.aprendiz.nombre, "Juan Pérez")
        self.assertEqual(self.aprendiz.estado, "DISPONIBLE")

    def test_aprendiz_string_representation(self):
        """Verificar representación en string"""
        expected = "Juan Pérez - juan@example.com"
        self.assertEqual(str(self.aprendiz), expected)


class EmpresaModelTest(TestCase):
    """Test cases para el modelo Empresa"""

    def setUp(self):
        """Crear empresa de prueba"""
        self.empresa = Empresa.objects.create(
            nombre="Tech Solutions",
            nit="123456789",
            estado="DISPONIBLE",
            capacidad_cupos=5,
        )

    def test_empresa_creation(self):
        """Verificar creación de empresa"""
        self.assertEqual(self.empresa.nombre, "Tech Solutions")
        self.assertEqual(self.empresa.capacidad_cupos, 5)


class PostulacionModelTest(TestCase):
    """Test cases para el modelo Postulacion"""

    def setUp(self):
        """Crear aprendiz, empresa y postulación de prueba"""
        self.aprendiz = Aprendiz.objects.create(
            nombre="María García",
            correo="maria@example.com",
            telefono="3009876543",
            estado="DISPONIBLE",
        )
        self.empresa = Empresa.objects.create(
            nombre="Innovatech",
            nit="987654321",
            capacidad_cupos=3,
            estado="DISPONIBLE",
        )
        self.postulacion = Postulacion.objects.create(
            aprendiz=self.aprendiz, empresa=self.empresa, estado="PENDIENTE"
        )

    def test_postulacion_creation(self):
        """Verificar creación de postulación"""
        self.assertEqual(self.postulacion.aprendiz, self.aprendiz)
        self.assertEqual(self.postulacion.empresa, self.empresa)
        self.assertEqual(self.postulacion.estado, "PENDIENTE")
