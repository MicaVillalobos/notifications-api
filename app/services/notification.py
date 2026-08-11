import logging

from app.channels.registry import get_canal
from app.models.enums import EstadoEnvio
from app.models.notification import Notification
from app.repositories.notification import NotificationRepository
from app.schemas.notification import NotificationCreate, NotificationUpdate

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    def create(self, data: NotificationCreate, user_id: int) -> Notification:
        notification = Notification(
            title=data.title,
            content=data.content,
            channel=data.channel,
            user_id=user_id,
        )
        notification = self.repository.create(notification)

        self._enviar(notification)

        return self.repository.update(notification)

    def list_mine(self, user_id: int) -> list[Notification]:
        return self.repository.list_by_user(user_id)

    def get(self, notification_id: int, user_id: int) -> Notification | None:
        return self.repository.get_by_id(notification_id, user_id)

    def update(
        self, notification_id: int, data: NotificationUpdate, user_id: int
    ) -> Notification | None:
        notification = self.repository.get_by_id(notification_id, user_id)
        if notification is None:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notification, field, value)

        return self.repository.update(notification)

    def delete(self, notification_id: int, user_id: int) -> bool:
        notification = self.repository.get_by_id(notification_id, user_id)
        if notification is None:
            return False

        self.repository.delete(notification)
        return True

    def _enviar(self, notification: Notification) -> None:
        try:
            canal = get_canal(notification.channel)
            canal.enviar(notification)
            notification.status = EstadoEnvio.ENVIADO
        except Exception:
            logger.exception("Fallo el envio de la notificacion id=%s", notification.id)
            notification.status = EstadoEnvio.FALLIDO