import logging

from app.channels.base import Canal
from app.models.notification import Notification

logger = logging.getLogger(__name__)

SMS_MAX_LENGTH = 160


class SmsChannel(Canal):
    def enviar(self, notification: Notification) -> None:
        # 1. Limitar el contenido a 160 caracteres
        contenido = self._truncar_contenido(notification.content)
        # 2. Registrar número y fecha de envío
        logger.info(
            "SMS enviado | destinatario=%s | contenido=%s",
            notification.user_id,
            contenido,
        )

    def _truncar_contenido(self, content: str) -> str:
        if len(content) > SMS_MAX_LENGTH:
            return content[:SMS_MAX_LENGTH]
        return content
