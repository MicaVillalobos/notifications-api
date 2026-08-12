from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Token, UserCreate, UserLogin


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def register(self, data: UserCreate) -> User:
        existing = self.repository.get_by_email(data.email)
        if existing is not None:
            raise ValueError("El email ya está registrado")

        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return self.repository.create(user)

    def login(self, data: UserLogin) -> Token:
        user = self.repository.get_by_email(data.email)
        if user is None or not verify_password(data.password, user.hashed_password):
            raise ValueError("Credenciales inválidas")

        token_data = {"sub": str(user.id)}
        return Token(
            access_token=create_access_token(token_data),
            refresh_token=create_refresh_token(token_data),
        )
