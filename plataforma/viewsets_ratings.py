"""
ViewSets para calificaciones
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from plataforma.models_ratings import Calificacion, PromedioCalificacion
from plataforma.serializers_ratings import (
    CalificacionSerializer,
    PromedioCalificacionSerializer,
)


class CalificacionViewSet(viewsets.ModelViewSet):
    """
    ViewSet para calificaciones
    POST /api/calificaciones/ - Crear calificación
    GET /api/calificaciones/{id}/ - Ver calificación
    PUT /api/calificaciones/{id}/ - Actualizar
    DELETE /api/calificaciones/{id}/ - Eliminar
    """

    queryset = Calificacion.objects.all()
    serializer_class = CalificacionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Asignar automáticamente el usuario actual como calificador"""
        serializer.save(calificador=self.request.user)

        # Actualizar promedio
        postulacion = serializer.instance.postulacion
        if serializer.instance.tipo == "EMPRESA_A_APRENDIZ":
            promedio, _ = PromedioCalificacion.objects.get_or_create(
                tipo="APRENDIZ", aprendiz=postulacion.aprendiz
            )
        else:
            promedio, _ = PromedioCalificacion.objects.get_or_create(
                tipo="EMPRESA", empresa=postulacion.empresa
            )
        promedio.actualizar_promedio()

    @action(detail=False, methods=["get"])
    def mis_calificaciones(self, request):
        """Obtener mis calificaciones como calificador"""
        calificaciones = Calificacion.objects.filter(calificador=request.user)
        serializer = self.get_serializer(calificaciones, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def calificaciones_recibidas(self, request):
        """Obtener calificaciones que he recibido"""
        # Determinar si es aprendiz o empresa
        aprendiz = getattr(request.user, "aprendiz", None)
        empresa = getattr(request.user, "empresa", None)

        if aprendiz:
            calificaciones = Calificacion.objects.filter(
                postulacion__aprendiz=aprendiz, tipo="EMPRESA_A_APRENDIZ"
            )
        elif empresa:
            calificaciones = Calificacion.objects.filter(
                postulacion__empresa=empresa, tipo="APRENDIZ_A_EMPRESA"
            )
        else:
            calificaciones = Calificacion.objects.none()

        serializer = self.get_serializer(calificaciones, many=True)
        return Response(serializer.data)


class PromedioCalificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para promedios de calificación (solo lectura)
    GET /api/promedios/ - Listar todos
    GET /api/promedios/{id}/ - Detalle
    """

    queryset = PromedioCalificacion.objects.all()
    serializer_class = PromedioCalificacionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=["get"])
    def mi_promedio(self, request):
        """Obtener mi promedio de calificación"""
        aprendiz = getattr(request.user, "aprendiz", None)
        empresa = getattr(request.user, "empresa", None)

        if aprendiz:
            try:
                promedio = PromedioCalificacion.objects.get(
                    tipo="APRENDIZ", aprendiz=aprendiz
                )
            except PromedioCalificacion.DoesNotExist:
                return Response(
                    {
                        "promedio": 0,
                        "total_calificaciones": 0,
                        "mensaje": "Sin calificaciones aún",
                    }
                )
        elif empresa:
            try:
                promedio = PromedioCalificacion.objects.get(
                    tipo="EMPRESA", empresa=empresa
                )
            except PromedioCalificacion.DoesNotExist:
                return Response(
                    {
                        "promedio": 0,
                        "total_calificaciones": 0,
                        "mensaje": "Sin calificaciones aún",
                    }
                )
        else:
            return Response({"error": "Usuario no es aprendiz ni empresa"})

        serializer = self.get_serializer(promedio)
        return Response(serializer.data)
