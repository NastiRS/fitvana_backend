import uuid
from datetime import datetime, date as date_type
from typing import Optional, Dict, Any

from sqlmodel import SQLModel

from app.domain.models.user import UserRole, Gender, Language, Currency


class UserBaseSchema(SQLModel):
    """
    Esquema base con campos comunes para Crear y Actualizar.
    """

    # Información Personal
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date_type] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    # Información Profesional/Social
    occupation: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    social_media: Optional[Dict[str, Any]] = None

    # Configuraciones y Preferencias
    timezone: Optional[str] = None
    language: Optional[Language] = None
    email_notifications: Optional[bool] = None
    currency_preference: Optional[Currency] = None
    accessibility_settings: Optional[Dict[str, Any]] = None


class UserCreateSchema(UserBaseSchema):
    """
    Esquema para crear un nuevo usuario. Requiere email, full_name y password.
    """

    email: str
    full_name: str
    password: str
    role: UserRole = UserRole.USER
    language: Language = Language.ES
    currency_preference: Currency = Currency.CUP


class UserReadSchema(UserBaseSchema):
    """
    Esquema para leer datos de usuario. Incluye todos los campos excepto la contraseña.
    """

    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    gender: Optional[Gender] = None
    language: Optional[Language] = Language.ES
    currency_preference: Optional[Currency] = Currency.CUP
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None
    terms_accepted_at: Optional[datetime] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class UserReadPublicSchema(SQLModel):
    """
    Esquema para mostrar información pública del usuario.
    Solo campos que pueden ser vistos por otros usuarios.
    """

    id: uuid.UUID
    username: Optional[str] = None
    full_name: str
    gender: Optional[Gender] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    occupation: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    social_media: Optional[Dict[str, Any]] = None


class UserUpdateSchema(UserBaseSchema):
    """
    Esquema para actualizar un usuario existente. Todos los campos son opcionales.
    """

    pass


class UserUpdatePasswordSchema(SQLModel):
    """
    Esquema para actualizar la contraseña de un usuario.
    """

    current_password: str
    new_password: str


class UserAcceptTermsSchema(SQLModel):
    """
    Esquema para aceptar términos y condiciones.
    """

    accept_terms: bool
    accept_privacy_policy: bool


class UserLoginSchema(SQLModel):
    """
    Esquema para login de usuario.
    """

    email: str
    password: str


class UserRoleUpdateSchema(SQLModel):
    """
    Esquema para cambiar el rol de un usuario (solo admin).
    """

    role: UserRole


class UserLanguageUpdateSchema(SQLModel):
    """
    Esquema para cambiar el idioma de un usuario.
    """

    language: Language


class UserCurrencyUpdateSchema(SQLModel):
    """
    Esquema para cambiar la moneda preferida de un usuario.
    """

    currency_preference: Currency
