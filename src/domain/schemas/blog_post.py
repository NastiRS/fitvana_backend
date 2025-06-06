import uuid
from datetime import date as date_type
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel

if TYPE_CHECKING:
    from src.domain.schemas.category import CategoryReadSchema
    from src.domain.schemas.section import SectionReadWithoutBlogPost
    from src.domain.schemas.tag import TagReadSchema


class BlogPostBaseSchema(SQLModel):
    """Esquema base con campos comunes para Crear y Actualizar.
    """

    title: str | None = None
    content: str | None = None
    date: date_type | None = None
    category_id: uuid.UUID | None = None


class BlogPostCreateSchema(BlogPostBaseSchema):
    """Esquema para crear un nuevo blog_post. Requiere título, contenido y category_id.
    """

    title: str
    content: str
    category_id: uuid.UUID


class BlogPostUpdateSchema(BlogPostBaseSchema):
    """Esquema para actualizar un blog_post. Todos los campos son opcionales.
    Hereda todos los campos de BlogPostBaseSchema, haciéndolos opcionales por defecto.
    """



class BlogPostReadSchema(BlogPostBaseSchema):
    """Esquema para leer/devolver datos de un blog_post desde la API.
    Incluye campos heredados del modelo Base (id, created_at, updated_at).
    """

    id: uuid.UUID
    title: str
    content: str
    category_id: uuid.UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    category: Optional["CategoryReadSchema"] = None
    tags: list["TagReadSchema"] = []
    sections: list["SectionReadWithoutBlogPost"] = []


from src.domain.schemas.category import CategoryReadSchema  # noqa: E402
from src.domain.schemas.section import SectionReadWithoutBlogPost  # noqa: E402
from src.domain.schemas.tag import TagReadSchema  # noqa: E402

BlogPostReadSchema.model_rebuild()
