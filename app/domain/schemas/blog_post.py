import uuid
from datetime import date as date_type, datetime
from typing import Optional, List, TYPE_CHECKING

from sqlmodel import SQLModel

if TYPE_CHECKING:
    from app.domain.schemas.category import CategoryReadSchema
    from app.domain.schemas.tag import TagReadSchema
    from app.domain.schemas.section import SectionReadWithoutBlogPost


class BlogPostBaseSchema(SQLModel):
    """
    Esquema base con campos comunes para Crear y Actualizar.
    """

    title: Optional[str] = None
    content: Optional[str] = None
    date: Optional[date_type] = None
    category_id: Optional[uuid.UUID] = None


class BlogPostCreateSchema(BlogPostBaseSchema):
    """
    Esquema para crear un nuevo blog_post. Requiere título, contenido y category_id.
    """

    title: str
    content: str
    category_id: uuid.UUID


class BlogPostUpdateSchema(BlogPostBaseSchema):
    """
    Esquema para actualizar un blog_post. Todos los campos son opcionales.
    Hereda todos los campos de BlogPostBaseSchema, haciéndolos opcionales por defecto.
    """

    pass


class BlogPostReadSchema(BlogPostBaseSchema):
    """
    Esquema para leer/devolver datos de un blog_post desde la API.
    Incluye campos heredados del modelo Base (id, created_at, updated_at).
    """

    id: uuid.UUID
    title: str
    content: str
    category_id: uuid.UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    category: Optional["CategoryReadSchema"] = None
    tags: List["TagReadSchema"] = []
    sections: List["SectionReadWithoutBlogPost"] = []


from app.domain.schemas.category import CategoryReadSchema  # noqa: E402
from app.domain.schemas.tag import TagReadSchema  # noqa: E402
from app.domain.schemas.section import SectionReadWithoutBlogPost  # noqa: E402

BlogPostReadSchema.model_rebuild()
