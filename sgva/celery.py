"""
Configuración de Celery para SGVA
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sgva.settings")

app = Celery("sgva")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Configuración de Celery Beat
app.conf.beat_schedule = {
    "recordar-vencimientos": {
        "task": "plataforma.tasks.recordar_postulaciones_vencidas",
        "schedule": crontab(hour=9, minute=0),
    },
    "limpiar-vencidas": {
        "task": "plataforma.tasks.limpiar_postulaciones_vencidas",
        "schedule": crontab(hour=0, minute=0),
    },
}


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
