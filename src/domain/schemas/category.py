import uuid

from sqlmodel import SQLModel


class CategoryBaseSchema(SQLModel):
    """Esquema base para categorías.
    """

    name: str
    description: str | None = None


class CategoryCreateSchema(CategoryBaseSchema):
    """Esquema para crear una nueva categoría.
    """



class CategoryUpdateSchema(CategoryBaseSchema):
    """Esquema para actualizar una categoría. Todos los campos son opcionales.
    """

    name: str | None = None
    description: str | None = None


class CategoryReadSchema(CategoryBaseSchema):
    """Esquema para leer/devolver datos de una categoría desde la API.
    """

    id: uuid.UUID
