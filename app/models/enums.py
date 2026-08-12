import enum


class CanalTipo(enum.StrEnum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class EstadoEnvio(enum.StrEnum):
    PENDIENTE = "pendiente"
    ENVIADO = "enviado"
    FALLIDO = "fallido"
