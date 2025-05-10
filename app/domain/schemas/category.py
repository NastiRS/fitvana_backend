import uuid
from typing import Optional

from sqlmodel import SQLModel


class CategoryBaseSchema(SQLModel):
    """
    Esquema base para categorías.
    """

    name: str
    description: Optional[str] = None


class CategoryCreateSchema(CategoryBaseSchema):
    """
    Esquema para crear una nueva categoría.
    """

    pass


class CategoryUpdateSchema(CategoryBaseSchema):
    """
    Esquema para actualizar una categoría. Todos los campos son opcionales.
    """

    name: Optional[str] = None
    description: Optional[str] = None


class CategoryReadSchema(CategoryBaseSchema):
    """
    Esquema para leer/devolver datos de una categoría desde la API.
    """

    id: uuid.UUID
