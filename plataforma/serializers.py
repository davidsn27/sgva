"""
API Serializers para la plataforma SGVA
"""

from rest_framework import serializers

from plataforma.models import (
    Aprendiz,
    Empresa,
    HistorialPostulacion,
    Postulacion,
)


class AprendizSerializer(serializers.ModelSerializer):
    """Serializer para modelo Aprendiz"""

    class Meta:
        model = Aprendiz
        fields = [
            "id",
            "nombre",
            "correo",
            "telefono",
            "estado",
            "ficha",
            "programa_formacion",
            "empresa_actual",
            "fecha_ultima_actividad",
        ]
        read_only_fields = ["id", "fecha_ultima_actividad"]


class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer para modelo Empresa"""

    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    cupos_disponibles = serializers.SerializerMethodField()

    class Meta:
        model = Empresa
        fields = [
            "id",
            "usuario",
            "usuario_username",
            "nit",
            "nombre",
            "descripcion",
            "direccion",
            "estado",
            "capacidad_cupos",
            "cupos_disponibles",
            "telefono_contacto",
            "correo_contacto",
            "observacion",
        ]
        read_only_fields = ["id", "cupos_disponibles"]

    def get_cupos_disponibles(self, obj) -> int:
        """Calcula cupos disponibles dinámicamente"""
        return obj.cupos_disponibles()


class PostulacionListSerializer(serializers.ModelSerializer):
    """Serializer simple para listar postulaciones"""

    aprendiz_nombre = serializers.SerializerMethodField()
    empresa_nombre = serializers.CharField(source="empresa.nombre", read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Postulacion
        fields = [
            "id",
            "aprendiz",
            "aprendiz_nombre",
            "empresa",
            "empresa_nombre",
            "estado",
            "fecha_postulacion",
            "dias_restantes",
        ]
        read_only_fields = ["id", "fecha_postulacion", "dias_restantes"]

    def get_aprendiz_nombre(self, obj) -> str:
        return getattr(obj.aprendiz, "nombre", str(obj.aprendiz))


class PostulacionDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para postulaciones"""

    aprendiz = AprendizSerializer(read_only=True)
    empresa = EmpresaSerializer(read_only=True)
    aprendiz_id = serializers.IntegerField(write_only=True)
    empresa_id = serializers.IntegerField(write_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Postulacion
        fields = [
            "id",
            "aprendiz",
            "aprendiz_id",
            "empresa",
            "empresa_id",
            "estado",
            "fecha_postulacion",
            "aprendiz_dio_respuesta",
            "dias_restantes",
        ]
        read_only_fields = ["id", "fecha_postulacion", "dias_restantes"]

    def create(self, validated_data):
        """Crear nueva postulación"""
        aprendiz_id = validated_data.pop("aprendiz_id")
        empresa_id = validated_data.pop("empresa_id")

        aprendiz = Aprendiz.objects.get(id=aprendiz_id)
        empresa = Empresa.objects.get(id=empresa_id)

        postulacion = Postulacion.objects.create(
            aprendiz=aprendiz, empresa=empresa, **validated_data
        )
        return postulacion


class HistorialPostulacionSerializer(serializers.ModelSerializer):
    """Serializer para historial de postulaciones"""

    class Meta:
        model = HistorialPostulacion
        fields = [
            "id",
            "postulacion",
            "estado_anterior",
            "estado_nuevo",
            "fecha_cambio",
        ]
        read_only_fields = ["id", "fecha_cambio"]
