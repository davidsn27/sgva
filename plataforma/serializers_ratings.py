"""
Serializers para calificaciones
"""

from rest_framework import serializers

from plataforma.models_ratings import Calificacion, PromedioCalificacion


class CalificacionSerializer(serializers.ModelSerializer):
    """Serializer para calificaciones"""

    calificador_nombre = serializers.CharField(
        source="calificador.get_full_name", read_only=True
    )

    class Meta:
        model = Calificacion
        fields = [
            "id",
            "postulacion",
            "tipo",
            "calificador",
            "calificador_nombre",
            "puntuacion",
            "comentario",
            "fecha_creacion",
        ]
        read_only_fields = ["id", "fecha_creacion", "calificador_nombre"]


class PromedioCalificacionSerializer(serializers.ModelSerializer):
    """Serializer para promedios de calificación"""

    class Meta:
        model = PromedioCalificacion
        fields = ["id", "tipo", "promedio", "total_calificaciones"]
        read_only_fields = ["id", "promedio", "total_calificaciones"]
