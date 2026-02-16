"""
Rutas de WebSocket para la aplicación
"""

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/notificaciones/(?P<usuario_id>\w+)/$",
        consumers.NotificacionConsumer.as_asgi(),
    ),
]
