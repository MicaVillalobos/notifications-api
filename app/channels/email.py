import logging

from app.channels.base import Canal
from app.models.notification import Notification

logger = logging.getLogger(__name__)


class EmailChannel(Canal):
    def enviar(self, notification: Notification) -> None:
        # 1. Validar el formato del destinatario
        self._validar_destinatario(notification)
        # 2. Generar el template
        cuerpo = self._generar_template(notification)
        # 3. Registrar el envío
        logger.info("Email enviado | destinatario=%s | cuerpo=%s", notification.user_id, cuerpo)

    def _validar_destinatario(self, notification: Notification) -> None:
        if not notification.title or not notification.content:
            raise ValueError("La notificación no tiene contenido para enviar por email")

    def _generar_template(self, notification: Notification) -> str:
        return f"<h1>{notification.title}</h1><p>{notification.content}</p>"