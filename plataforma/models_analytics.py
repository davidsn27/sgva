"""
Modelos para analytics y estadísticas
"""

from django.db import models
from django.utils import timezone

from plataforma.models import Aprendiz, Empresa, Postulacion


class EstadisticaDiaria(models.Model):
    """Estadísticas agregadas diarias"""

    fecha = models.DateField(auto_now_add=True, unique=True, db_index=True)

    # Usuarios
    total_aprendices = models.IntegerField(default=0)
    total_empresas = models.IntegerField(default=0)
    aprendices_activos = models.IntegerField(default=0)
    empresas_activas = models.IntegerField(default=0)

    # Postulaciones
    total_postulaciones = models.IntegerField(default=0)
    postulaciones_nuevas = models.IntegerField(default=0)
    postulaciones_seleccionadas = models.IntegerField(default=0)
    postulaciones_rechazadas = models.IntegerField(default=0)
    postulaciones_pendientes = models.IntegerField(default=0)

    # Tasa de conversión
    tasa_conversion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Porcentaje de postulaciones seleccionadas",
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Estadísticas {self.fecha}"

    @classmethod
    def actualizar_hoy(cls):
        """Actualizar o crear estadísticas de hoy"""
        hoy = timezone.now().date()

        stats, _ = cls.objects.get_or_create(fecha=hoy)

        # Contar usuarios
        stats.total_aprendices = Aprendiz.objects.count()
        stats.total_empresas = Empresa.objects.count()
        stats.aprendices_activos = Aprendiz.objects.exclude(
            estado="INHABILITADO_POR_ACTUALIZACION"
        ).count()
        stats.empresas_activas = Empresa.objects.filter(estado="DISPONIBLE").count()

        # Contar postulaciones
        stats.total_postulaciones = Postulacion.objects.count()
        stats.postulaciones_nuevas = Postulacion.objects.filter(
            fecha_postulacion__date=hoy
        ).count()
        stats.postulaciones_seleccionadas = Postulacion.objects.filter(
            estado__in=[
                "SELECCIONADO",
                "PROCESO_SELECCION_ABIERTO",
                "CONTRATADO",
            ]
        ).count()
        stats.postulaciones_rechazadas = Postulacion.objects.filter(
            estado__in=["RECHAZADO", "CONTRATO_NO_REGISTRADO"]
        ).count()
        stats.postulaciones_pendientes = Postulacion.objects.filter(
            estado="PENDIENTE"
        ).count()

        # Calcular tasa de conversión
        if stats.total_postulaciones > 0:
            stats.tasa_conversion = (
                stats.postulaciones_seleccionadas / stats.total_postulaciones
            ) * 100

        stats.save()
        return stats


class MetricaPersonalizada(models.Model):
    """Métricas personalizadas que el usuario puede definir"""

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    tipo = models.CharField(
        max_length=50,
        choices=[
            ("CONTADOR", "Contador"),
            ("PROMEDIO", "Promedio"),
            ("PORCENTAJE", "Porcentaje"),
            ("TIEMPO", "Tiempo"),
        ],
    )

    valor = models.FloatField()
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_actualizacion"]

    def __str__(self):
        return f"{self.nombre}: {self.valor}"
