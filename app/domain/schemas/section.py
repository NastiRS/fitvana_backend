import uuid
from typing import Optional

from sqlmodel import SQLModel


class SectionBaseSchema(SQLModel):
    """
    Esquema base para secciones.
    """

    title: str
    image_url: Optional[str] = None
    content: str
    position_order: int = 0
    blog_post_id: uuid.UUID


class SectionCreateSchema(SectionBaseSchema):
    """
    Esquema para crear una nueva sección.
    """

    pass


class SectionUpdateSchema(SQLModel):
    """
    Esquema para actualizar una sección. Todos los campos son opcionales.
    """

    title: Optional[str] = None
    image_url: Optional[str] = None
    content: Optional[str] = None
    position_order: Optional[int] = None
    blog_post_id: Optional[uuid.UUID] = None


class SectionReadSchema(SectionBaseSchema):
    """
    Esquema para leer/devolver datos de una sección desde la API.
    """

    id: uuid.UUID


class SectionReadWithoutBlogPost(SQLModel):
    """
    Esquema para leer secciones sin incluir el blog_post completo (evita referencias circulares).
    """

    id: uuid.UUID
    title: str
    image_url: Optional[str] = None
    content: str
    position_order: int
