import logging

from app.channels.base import Canal
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class PushChannel(Canal):
    def enviar(self, notification: Notification) -> None:
        # 1. Validar el token de dispositivo
        self._validar_token_dispositivo(notification)
        # 2. Formatear el payload
        payload = self._formatear_payload(notification)
        # 3. Registrar el estado del envío
        logger.info("Push enviado | destinatario=%s | payload=%s", notification.user_id, payload)

    def _validar_token_dispositivo(self, notification: Notification) -> None:
        # En un sistema real validaríamos el token del dispositivo del usuario.
        # Ese dato no vive en la notificación, así que acá simulamos el paso.
        pass

    def _formatear_payload(self, notification: Notification) -> dict:
        return {
            "title": notification.title,
            "body": notification.content,
            "channel": notification.channel.value,
        }