"""
Tests para API REST
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from plataforma.models import Aprendiz, Empresa, Postulacion


@pytest.mark.django_db
class TestAprendizAPI:
    """Tests para endpoint de Aprendices"""

    def setup_method(self):
        """Preparación para cada test"""
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username="aprendiz1",
            email="aprendiz@test.com",
            password="test123456",
        )
        self.aprendiz = Aprendiz.objects.create(
            usuario=self.usuario,
            nombres="Juan",
            apellidos="Pérez",
            email="juan@test.com",
            numero_identificacion="123456789",
            estado="DISPONIBLE",
        )

    def test_list_aprendices(self):
        """Probar obtener lista de aprendices"""
        response = self.client.get("/api/aprendices/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["nombres"] == "Juan"

    def test_create_aprendiz(self):
        """Probar crear nuevo aprendiz"""
        nuevo_usuario = User.objects.create_user(
            username="aprendiz2",
            email="aprendiz2@test.com",
            password="test123456",
        )

        data = {
            "usuario": nuevo_usuario.id,
            "nombres": "María",
            "apellidos": "García",
            "email": "maria@test.com",
            "numero_identificacion": "987654321",
            "estado": "DISPONIBLE",
        }

        response = self.client.post("/api/aprendices/", data, format="json")
        assert response.status_code == 201
        assert response.data["nombres"] == "María"

    def test_retrieve_aprendiz(self):
        """Probar obtener detalle de aprendiz"""
        response = self.client.get(f"/api/aprendices/{self.aprendiz.id}/")
        assert response.status_code == 200
        assert response.data["nombres"] == "Juan"

    def test_activos_filter(self):
        """Probar filtro de aprendices activos"""
        response = self.client.get("/api/aprendices/activos/")
        assert response.status_code == 200
        assert len(response.data) == 1


@pytest.mark.django_db
class TestEmpresaAPI:
    """Tests para endpoint de Empresas"""

    def setup_method(self):
        """Preparación para cada test"""
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username="empresa1",
            email="empresa@test.com",
            password="test123456",
        )
        self.empresa = Empresa.objects.create(
            usuario=self.usuario,
            nit="123456789",
            nombre="Tech Solutions",
            estado="DISPONIBLE",
            capacidad_cupos=5,
        )

    def test_list_empresas(self):
        """Probar obtener lista de empresas"""
        response = self.client.get("/api/empresas/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["nombre"] == "Tech Solutions"

    def test_empresa_cupos_disponibles(self):
        """Probar cálculo de cupos disponibles"""
        response = self.client.get(f"/api/empresas/{self.empresa.id}/")
        assert response.status_code == 200
        assert response.data["cupos_disponibles"] == 5

    def test_disponibles_filter(self):
        """Probar filtro de empresas disponibles"""
        response = self.client.get("/api/empresas/disponibles/")
        assert response.status_code == 200
        assert len(response.data) == 1


@pytest.mark.django_db
class TestPostulacionAPI:
    """Tests para endpoint de Postulaciones"""

    def setup_method(self):
        """Preparación para cada test"""
        self.client = APIClient()

        # Crear aprendiz
        usuario_aprendiz = User.objects.create_user(
            username="aprendiz1",
            email="aprendiz@test.com",
            password="test123456",
        )
        self.aprendiz = Aprendiz.objects.create(
            usuario=usuario_aprendiz,
            nombres="Juan",
            apellidos="Pérez",
            email="juan@test.com",
            numero_identificacion="123456789",
            estado="DISPONIBLE",
        )

        # Crear empresa
        usuario_empresa = User.objects.create_user(
            username="empresa1",
            email="empresa@test.com",
            password="test123456",
        )
        self.empresa = Empresa.objects.create(
            usuario=usuario_empresa,
            nit="123456789",
            nombre="Tech Solutions",
            estado="DISPONIBLE",
            capacidad_cupos=5,
        )

        # Crear postulación
        self.postulacion = Postulacion.objects.create(
            aprendiz=self.aprendiz, empresa=self.empresa, estado="PENDIENTE"
        )

    def test_list_postulaciones(self):
        """Probar obtener lista de postulaciones"""
        response = self.client.get("/api/postulaciones/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1

    def test_cambiar_estado_postulacion(self):
        """Probar cambiar estado de postulación"""
        data = {"estado": "SELECCIONADO"}
        response = self.client.post(
            f"/api/postulaciones/{self.postulacion.id}/cambiar_estado/",
            data,
            format="json",
        )
        assert response.status_code == 200
        assert response.data["estado"] == "SELECCIONADO"

    def test_vencidas_filter(self):
        """Probar filtro de postulaciones vencidas"""
        response = self.client.get("/api/postulaciones/vencidas/")
        assert response.status_code == 200
