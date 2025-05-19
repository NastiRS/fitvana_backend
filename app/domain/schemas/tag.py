import uuid
from typing import Optional

from sqlmodel import SQLModel


class TagBaseSchema(SQLModel):
    """
    Esquema base para tags.
    """

    name: str


class TagCreateSchema(TagBaseSchema):
    """
    Esquema para crear un nuevo tag.
    """

    pass


class TagUpdateSchema(TagBaseSchema):
    """
    Esquema para actualizar un tag. Todos los campos son opcionales.
    """

    name: Optional[str] = None


class TagReadSchema(TagBaseSchema):
    """
    Esquema para leer/devolver datos de un tag desde la API.
    """

    id: uuid.UUID
