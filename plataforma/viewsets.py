"""
API ViewSets para la plataforma SGVA
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from plataforma.models import (
    Aprendiz,
    Empresa,
    HistorialPostulacion,
    Postulacion,
)
from plataforma.serializers import (
    AprendizSerializer,
    EmpresaSerializer,
    HistorialPostulacionSerializer,
    PostulacionDetailSerializer,
    PostulacionListSerializer,
)


class AprendizViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Aprendices
    GET /api/aprendices/ - Listar todos
    POST /api/aprendices/ - Crear nuevo
    GET /api/aprendices/{id}/ - Detalle
    PUT /api/aprendices/{id}/ - Actualizar
    DELETE /api/aprendices/{id}/ - Eliminar
    """

    queryset = Aprendiz.objects.all()
    serializer_class = AprendizSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["estado"]
    search_fields = ["nombre", "correo", "telefono", "ficha"]
    ordering_fields = ["fecha_ultima_actividad", "nombre"]
    ordering = ["-fecha_ultima_actividad"]

    @action(detail=True, methods=["get"])
    def postulaciones(self, request, pk=None):
        """Obtener todas las postulaciones de un aprendiz"""
        aprendiz = self.get_object()
        postulaciones = aprendiz.postulacion_set.all()  # noqa: E501
        serializer = PostulacionListSerializer(postulaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def activos(self, request):
        """Obtener solo aprendices activos"""
        aprendices = Aprendiz.objects.exclude(estado="INHABILITADO_POR_ACTUALIZACION")
        serializer = self.get_serializer(aprendices, many=True)
        return Response(serializer.data)


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Empresas
    GET /api/empresas/ - Listar todos
    POST /api/empresas/ - Crear nueva
    GET /api/empresas/{id}/ - Detalle
    PUT /api/empresas/{id}/ - Actualizar
    DELETE /api/empresas/{id}/ - Eliminar
    """

    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["estado"]
    search_fields = ["nombre", "nit"]
    ordering_fields = ["nombre", "capacidad_cupos"]
    ordering = ["nombre"]

    @action(detail=True, methods=["get"])
    def postulaciones(self, request, pk=None):
        """Obtener todas las postulaciones recibidas por una empresa"""
        empresa = self.get_object()
        postulaciones = empresa.postulacion_set.all()
        serializer = PostulacionListSerializer(postulaciones, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def postulaciones_pendientes(self, request, pk=None):
        """Obtener postulaciones pendientes"""
        empresa = self.get_object()
        postulaciones = empresa.postulacion_set.filter(estado="PENDIENTE")
        serializer = PostulacionListSerializer(postulaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def disponibles(self, request):
        """Obtener solo empresas disponibles con cupos"""
        empresas = Empresa.objects.filter(estado="DISPONIBLE", capacidad_cupos__gt=0)
        serializer = self.get_serializer(empresas, many=True)
        return Response(serializer.data)


class PostulacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Postulaciones
    GET /api/postulaciones/ - Listar todos
    POST /api/postulaciones/ - Crear nueva
    GET /api/postulaciones/{id}/ - Detalle
    PUT /api/postulaciones/{id}/ - Actualizar
    DELETE /api/postulaciones/{id}/ - Eliminar
    """

    queryset = Postulacion.objects.all()
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["estado", "aprendiz", "empresa"]
    ordering_fields = ["fecha_postulacion", "estado"]
    ordering = ["-fecha_postulacion"]

    def get_serializer_class(self):
        """Usar serializer detallado o simple"""
        if self.action == "retrieve" or self.action == "create":
            return PostulacionDetailSerializer
        return PostulacionListSerializer

    @action(detail=True, methods=["post"])
    def cambiar_estado(self, request, pk=None):
        """Cambiar estado de postulación"""
        postulacion = self.get_object()
        nuevo_estado = request.data.get("estado")

        valid_states = [
            "PENDIENTE",
            "PROCESO_SELECCION_ABIERTO",
            "CONTRATO_NO_REGISTRADO",
            "CONTRATADO",
            "DISPONIBLE",
            # Compatibilidad/analytics
            "SELECCIONADO",
            "RECHAZADO",
        ]
        if nuevo_estado not in valid_states:
            return Response(
                {"error": "Estado inválido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        postulacion.estado = nuevo_estado  # noqa: E501
        postulacion.save()

        serializer = PostulacionDetailSerializer(postulacion)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def vencidas(self, request):
        """Obtener postulaciones vencidas (más de 15 días)"""
        from datetime import datetime, timedelta

        hace_15_dias = datetime.now() - timedelta(days=15)
        postulaciones = Postulacion.objects.filter(fecha_postulacion__lt=hace_15_dias)
        serializer = PostulacionListSerializer(postulaciones, many=True)
        return Response(serializer.data)


class HistorialPostulacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de solo lectura para Historial de Postulaciones
    GET /api/historial/ - Listar todos
    GET /api/historial/{id}/ - Detalle
    """

    queryset = HistorialPostulacion.objects.all()
    serializer_class = HistorialPostulacionSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["postulacion", "estado_nuevo"]
    ordering_fields = ["fecha_cambio"]
    ordering = ["-fecha_cambio"]
