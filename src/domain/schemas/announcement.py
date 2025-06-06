import uuid

from sqlmodel import SQLModel


class AnnouncementBaseSchema(SQLModel):
    """Esquema base para anuncios.
    """

    name: str
    url: str | None = None
    image_url: str | None = None


class AnnouncementCreateSchema(AnnouncementBaseSchema):
    """Esquema para crear un nuevo anuncio.
    """



class AnnouncementUpdateSchema(SQLModel):
    """Esquema para actualizar un anuncio. Todos los campos son opcionales.
    """

    name: str | None = None
    url: str | None = None
    image_url: str | None = None


class AnnouncementReadSchema(AnnouncementBaseSchema):
    """Esquema para leer/devolver datos de un anuncio desde la API.
    """

    id: uuid.UUID
