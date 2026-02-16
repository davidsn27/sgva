from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from plataforma.models import HistorialPostulacion, Postulacion


class Command(BaseCommand):
    help = "Cambia postulaciones a CONTRATO_NULO si han estado pendientes por más de 15 días hábiles sin respuesta"

    def handle(self, *args, **options):
        # Calcular la fecha de corte (hace 15 días hábiles)
        dias_habiles_a_restar = 15
        fecha_de_corte = timezone.now()
        dias_restados = 0

        while dias_restados < dias_habiles_a_restar:
            fecha_de_corte -= timedelta(days=1)
            # Lunes=0, ..., Sábado=5, Domingo=6
            if fecha_de_corte.weekday() < 5:
                dias_restados += 1

        # Buscar postulaciones pendientes hace más de 15 días sin respuesta de la empresa
        postulaciones = Postulacion.objects.filter(
            estado="PENDIENTE",
            fecha_postulacion__lte=fecha_de_corte,
            empresa_dio_respuesta=False,
        )

        count = 0
        for postulacion in postulaciones:
            estado_anterior = postulacion.estado
            postulacion.estado = "CONTRATO_NULO"
            postulacion.save()

            # Crear historial
            HistorialPostulacion.objects.create(
                postulacion=postulacion,
                estado_anterior=estado_anterior,
                estado_nuevo="CONTRATO_NULO",
                usuario=None,
                comentario="Automático: Más de 15 días hábiles sin respuesta de la empresa - Estado cambió a CONTRATO_NULO",
            )

            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Se cambiaron {count} postulaciones a CONTRATO_NULO")
        )
