from datetime import datetime, date as date_type
from typing import Optional
from enum import Enum

from sqlmodel import Field, JSON

from .base import Base


class Language(str, Enum):
    """
    Idiomas disponibles para usuarios.
    """

    ES = "es"
    EN = "en"


class Gender(str, Enum):
    """
    Géneros disponibles para usuarios.
    """

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class Currency(str, Enum):
    """
    Monedas disponibles para usuarios.
    """

    USD = "USD"
    EUR = "EUR"
    CUP = "CUP"


class UserRole(str, Enum):
    """
    Roles disponibles para usuarios.
    """

    USER = "user"
    OWNER = "owner"
    ADMIN = "admin"


class User(Base, table=True):
    # Información Personal
    email: str = Field(unique=True, index=True)
    username: Optional[str] = Field(default=None, unique=True, index=True)
    full_name: str
    phone: Optional[str] = Field(default=None)
    date_of_birth: Optional[date_type] = Field(default=None)
    gender: Optional[Gender] = Field(default=None)
    address: Optional[str] = Field(default=None)
    bio: Optional[str] = Field(default=None)
    avatar_url: Optional[str] = Field(default=None)

    # Autenticación y Seguridad
    hashed_password: str
    role: UserRole = Field(default=UserRole.USER)
    password_history: Optional[dict] = Field(default=None, sa_type=JSON)
    last_password_reset_request: Optional[datetime] = Field(default=None)
    last_login: Optional[datetime] = Field(default=None)

    # Estado del Usuario
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)

    # Información Profesional/Social
    occupation: Optional[str] = Field(default=None)
    company: Optional[str] = Field(default=None)
    website: Optional[str] = Field(default=None)
    location: Optional[str] = Field(default=None)
    social_media: Optional[dict] = Field(default=None, sa_type=JSON)

    # Configuraciones y Preferencias
    timezone: Optional[str] = Field(default="UTC")
    language: Optional[Language] = Field(default=Language.ES)
    email_notifications: bool = Field(default=True)
    currency_preference: Optional[Currency] = Field(default=Currency.CUP)
    accessibility_settings: Optional[dict] = Field(default=None, sa_type=JSON)

    # Términos y Políticas
    terms_accepted_at: Optional[datetime] = Field(default=None)
    privacy_policy_accepted_at: Optional[datetime] = Field(default=None)
