from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import CanalTipo, EstadoEnvio


class NotificationBase(BaseModel):
    title: str
    content: str
    channel: CanalTipo


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    channel: CanalTipo | None = None


class NotificationResponse(NotificationBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: EstadoEnvio
    user_id: int
    created_at: datetime
