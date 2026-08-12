from app.channels.base import Canal
from app.channels.email import EmailChannel
from app.channels.push import PushChannel
from app.channels.sms import SmsChannel
from app.models.enums import CanalTipo

CANALES: dict[CanalTipo, Canal] = {
    CanalTipo.EMAIL: EmailChannel(),
    CanalTipo.SMS: SmsChannel(),
    CanalTipo.PUSH: PushChannel(),
}


def get_canal(channel: CanalTipo) -> Canal:
    return CANALES[channel]
