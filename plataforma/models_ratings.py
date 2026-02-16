"""
Modelo de Calificaciones para aprendices y empresas
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from plataforma.models import Aprendiz, Empresa, Postulacion


class Calificacion(models.Model):
    """Calificaciones mutuas entre aprendices y empresas"""

    TIPOS = [
        ("EMPRESA_A_APRENDIZ", "Empresa califica a Aprendiz"),
        ("APRENDIZ_A_EMPRESA", "Aprendiz califica a Empresa"),
    ]

    postulacion = models.ForeignKey(
        Postulacion, on_delete=models.CASCADE, related_name="calificaciones"
    )
    tipo = models.CharField(max_length=20, choices=TIPOS)

    # Calificador
    calificador = models.ForeignKey("auth.User", on_delete=models.CASCADE)

    # Puntuación
    puntuacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Calificación de 1 a 5 estrellas",
    )

    # Comentario
    comentario = models.TextField(blank=True)

    # Metadata
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("postulacion", "tipo")
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.puntuacion}⭐"

    @property
    def aprendiz_calificado(self):
        """Retorna el aprendiz siendo calificado"""
        return self.postulacion.aprendiz

    @property
    def empresa_calificada(self):
        """Retorna la empresa siendo calificada"""
        return self.postulacion.empresa


class PromedioCalificacion(models.Model):
    """Promedio de calificaciones por aprendiz o empresa"""

    TIPOS = [
        ("APRENDIZ", "Aprendiz"),
        ("EMPRESA", "Empresa"),
    ]

    tipo = models.CharField(max_length=10, choices=TIPOS)
    aprendiz = models.OneToOneField(
        Aprendiz,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="promedio_calificacion",
    )
    empresa = models.OneToOneField(
        Empresa,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="promedio_calificacion",
    )

    promedio = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_calificaciones = models.IntegerField(default=0)

    class Meta:
        unique_together = ("tipo", "aprendiz", "empresa")

    def actualizar_promedio(self):
        """Actualizar el promedio basado en calificaciones"""
        if self.tipo == "APRENDIZ":
            calificaciones = Calificacion.objects.filter(
                postulacion__aprendiz=self.aprendiz, tipo="EMPRESA_A_APRENDIZ"
            )
        else:
            calificaciones = Calificacion.objects.filter(
                postulacion__empresa=self.empresa, tipo="APRENDIZ_A_EMPRESA"
            )

        if calificaciones.exists():
            self.promedio = (
                sum(c.puntuacion for c in calificaciones) / calificaciones.count()
            )
            self.total_calificaciones = calificaciones.count()

        self.save()

    def __str__(self):
        entity = self.aprendiz or self.empresa
        return (
            f"{entity} - {self.promedio}⭐ ({self.total_calificaciones} calificaciones)"
        )
