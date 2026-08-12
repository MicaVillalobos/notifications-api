from abc import ABC, abstractmethod

from app.models.notification import Notification


class Canal(ABC):
    @abstractmethod
    def enviar(self, notification: Notification) -> None: ...
