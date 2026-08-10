from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func

from app.database import Base
from app.models.enums import CanalTipo, EstadoEnvio


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel = Column(
    Enum(CanalTipo, values_callable=lambda enum_class: [member.value for member in enum_class]),
    nullable=False,)
    status = Column(
    Enum(EstadoEnvio, values_callable=lambda enum_class: [member.value for member in enum_class]),
    server_default=EstadoEnvio.PENDIENTE.value,
    nullable=False,)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)