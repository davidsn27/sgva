"""
Tareas de Celery para envío de emails asincrónico
"""

from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from plataforma.models import Postulacion


@shared_task
def enviar_email_postulacion(aprendiz_email, aprendiz_nombre, empresa_nombre):
    """Enviar email cuando aprendiz se postula"""
    asunto = f"Tu postulación a {empresa_nombre}"
    contexto = {
        "aprendiz_nombre": aprendiz_nombre,
        "empresa_nombre": empresa_nombre,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
    }

    html_message = render_to_string("emails/postulacion.html", contexto)
    plain_message = strip_tags(html_message)

    send_mail(
        asunto,
        plain_message,
        "noreply@sgva.local",
        [aprendiz_email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def enviar_email_cambio_estado(
    aprendiz_email, aprendiz_nombre, empresa_nombre, estado_nuevo
):
    """Enviar email cuando cambia estado de postulación"""
    estado_label = dict(
        {
            "PENDIENTE": "Pendiente",
            "SELECCIONADO": "¡Has sido seleccionado!",
            "RECHAZADO": "No has sido seleccionado",
        }
    ).get(estado_nuevo, estado_nuevo)

    asunto = f"Actualización de tu postulación a {empresa_nombre}"
    contexto = {
        "aprendiz_nombre": aprendiz_nombre,
        "empresa_nombre": empresa_nombre,
        "estado": estado_label,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
    }

    html_message = render_to_string("emails/cambio_estado.html", contexto)
    plain_message = strip_tags(html_message)

    send_mail(
        asunto,
        plain_message,
        "noreply@sgva.local",
        [aprendiz_email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def enviar_email_empresa_nueva_postulacion(
    empresa_email, empresa_nombre, aprendiz_nombre, aprendiz_email
):
    """Notificar a empresa sobre nueva postulación"""
    asunto = f"Nueva postulación de {aprendiz_nombre}"
    contexto = {
        "empresa_nombre": empresa_nombre,
        "aprendiz_nombre": aprendiz_nombre,
        "aprendiz_email": aprendiz_email,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
    }

    html_message = render_to_string("emails/nueva_postulacion_empresa.html", contexto)
    plain_message = strip_tags(html_message)

    send_mail(
        asunto,
        plain_message,
        "noreply@sgva.local",
        [empresa_email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def recordar_postulaciones_vencidas():
    """Tarea programada: recordar postulaciones que vencen pronto"""
    hace_14_dias = datetime.now() - timedelta(days=14)
    hace_15_dias = datetime.now() - timedelta(days=15)

    # Postulaciones que vencen en 1 día
    postulaciones_proximas = Postulacion.objects.filter(
        fecha_postulacion__gt=hace_14_dias,
        fecha_postulacion__lte=hace_14_dias,
        estado="PENDIENTE",
    )

    for postulacion in postulaciones_proximas:
        asunto = f"Tu postulación a {postulacion.empresa.nombre} vence pronto"
        contexto = {
            "aprendiz_nombre": postulacion.aprendiz.nombres,
            "empresa_nombre": postulacion.empresa.nombre,
            "dias_restantes": 1,
        }

        html_message = render_to_string(
            "emails/recordatorio_vencimiento.html", contexto
        )
        plain_message = strip_tags(html_message)

        send_mail(
            asunto,
            plain_message,
            "noreply@sgva.local",
            [postulacion.aprendiz.email],
            html_message=html_message,
            fail_silently=False,
        )


@shared_task
def limpiar_postulaciones_vencidas():
    """Tarea programada: marcar postulaciones como vencidas"""
    hace_15_dias = datetime.now() - timedelta(days=15)

    Postulacion.objects.filter(
        fecha_postulacion__lt=hace_15_dias, estado="PENDIENTE"
    ).update(estado="CONTRATO_NO_REGISTRADO")


# Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    "recordar-vencimientos": {
        "task": "plataforma.tasks.recordar_postulaciones_vencidas",
        "schedule": crontab(hour=9, minute=0),  # Cada día a las 9 AM
    },
    "limpiar-vencidas": {
        "task": "plataforma.tasks.limpiar_postulaciones_vencidas",
        "schedule": crontab(hour=0, minute=0),  # Cada día a media noche
    },
}
