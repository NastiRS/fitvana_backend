from typing import Annotated, Optional
from fastapi import Depends
from sqlmodel import Session, select
from datetime import datetime

from app.repository.base import BaseRepository
from app.domain.models.user import User
from app.domain.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.database.config import get_session


class UserRepository(BaseRepository[User, UserCreateSchema, UserUpdateSchema]):
    def __init__(self, model: type, db_session: Session):
        super().__init__(model, db_session)

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Obtiene un usuario por su email.
        """
        stmt = select(User).where(User.email == email)
        return self.session.exec(stmt).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Obtiene un usuario por su username.
        """
        stmt = select(User).where(User.username == username)
        return self.session.exec(stmt).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Obtiene todos los usuarios activos.
        """
        stmt = select(User).where(User.is_active == True).offset(skip).limit(limit)
        return list(self.session.exec(stmt).all())

    def get_users_by_role(
        self, role: str, skip: int = 0, limit: int = 100
    ) -> list[User]:
        """
        Obtiene usuarios por rol específico.
        """
        stmt = select(User).where(User.role == role).offset(skip).limit(limit)
        return list(self.session.exec(stmt).all())

    def get_unverified_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """
        Obtiene usuarios no verificados.
        """
        stmt = select(User).where(User.is_verified == False).offset(skip).limit(limit)
        return list(self.session.exec(stmt).all())

    def update_last_login(self, user: User) -> User:
        """
        Actualiza la fecha de último login del usuario.
        """
        user.last_login = datetime.now()
        try:
            self.session.add(user)
            self._save(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def update_password_reset_request(self, user: User) -> User:
        """
        Actualiza la fecha de la última solicitud de reset de contraseña.
        """
        user.last_password_reset_request = datetime.now()
        try:
            self.session.add(user)
            self._save(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def verify_user(self, user: User) -> User:
        """
        Marca al usuario como verificado.
        """
        user.is_verified = True
        try:
            self.session.add(user)
            self._save(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def accept_terms(
        self, user: User, accept_terms: bool = True, accept_privacy: bool = True
    ) -> User:
        """
        Actualiza la aceptación de términos y políticas.
        """
        now = datetime.now()
        if accept_terms:
            user.terms_accepted_at = now
        if accept_privacy:
            user.privacy_policy_accepted_at = now

        try:
            self.session.add(user)
            self._save(user)
            return user
        except Exception:
            self.session.rollback()
            raise


def get_user_repository(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(model=User, db_session=session)


CurrentUserRepo = Annotated[UserRepository, Depends(get_user_repository)]
