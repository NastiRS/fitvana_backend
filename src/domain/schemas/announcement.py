import uuid
from typing import Optional

from sqlmodel import SQLModel


class AnnouncementBaseSchema(SQLModel):
    """
    Esquema base para anuncios.
    """

    name: str
    url: Optional[str] = None
    image_url: Optional[str] = None


class AnnouncementCreateSchema(AnnouncementBaseSchema):
    """
    Esquema para crear un nuevo anuncio.
    """

    pass


class AnnouncementUpdateSchema(SQLModel):
    """
    Esquema para actualizar un anuncio. Todos los campos son opcionales.
    """

    name: Optional[str] = None
    url: Optional[str] = None
    image_url: Optional[str] = None


class AnnouncementReadSchema(AnnouncementBaseSchema):
    """
    Esquema para leer/devolver datos de un anuncio desde la API.
    """

    id: uuid.UUID
