"""
Consumer de WebSocket para notificaciones en tiempo real
Instalación: pip install channels daphne
"""

import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificacionConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para notificaciones en tiempo real

    Conexión: ws://localhost:8000/ws/notificaciones/usuario_id/
    """

    async def connect(self):
        """Cuando un cliente se conecta"""
        self.usuario_id = self.scope["url_route"]["kwargs"]["usuario_id"]
        self.room_group_name = f"notificaciones_{self.usuario_id}"

        # Agregar al grupo de WebSocket
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()
        print(f"✅ Usuario {self.usuario_id} conectado a WebSocket")

    async def disconnect(self, close_code):
        """Cuando un cliente se desconecta"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"❌ Usuario {self.usuario_id} desconectado")

    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        try:
            data = json.loads(text_data)
            tipo = data.get("type", "mensaje")

            if tipo == "ping":
                await self.send(
                    text_data=json.dumps({"type": "pong", "message": "Servidor activo"})
                )
        except json.JSONDecodeError:
            pass

    # Métodos para recibir eventos del grupo
    async def notificacion_postulacion(self, event):
        """Enviar notificación cuando hay nueva postulación"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notificacion_postulacion",
                    "aprendiz": event["aprendiz"],
                    "empresa": event["empresa"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def notificacion_cambio_estado(self, event):
        """Enviar notificación cuando cambia estado de postulación"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notificacion_cambio_estado",
                    "postulacion_id": event["postulacion_id"],
                    "estado_anterior": event["estado_anterior"],
                    "estado_nuevo": event["estado_nuevo"],
                    "timestamp": event["timestamp"],
                }
            )
        )

    async def notificacion_vencimiento(self, event):
        """Enviar notificación de vencimiento de postulación"""
        await self.send(
            text_data=json.dumps(
                {
                    "type": "notificacion_vencimiento",
                    "postulacion_id": event["postulacion_id"],
                    "mensaje": event["mensaje"],
                    "timestamp": event["timestamp"],
                }
            )
        )
