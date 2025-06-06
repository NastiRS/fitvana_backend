import uuid

from sqlmodel import SQLModel


class TagBaseSchema(SQLModel):
    """Esquema base para tags.
    """

    name: str


class TagCreateSchema(TagBaseSchema):
    """Esquema para crear un nuevo tag.
    """



class TagUpdateSchema(TagBaseSchema):
    """Esquema para actualizar un tag. Todos los campos son opcionales.
    """

    name: str | None = None


class TagReadSchema(TagBaseSchema):
    """Esquema para leer/devolver datos de un tag desde la API.
    """

    id: uuid.UUID
