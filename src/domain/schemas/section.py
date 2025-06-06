import uuid

from sqlmodel import SQLModel


class SectionBaseSchema(SQLModel):
    """Esquema base para secciones.
    """

    title: str
    image_url: str | None = None
    content: str
    position_order: int = 0
    blog_post_id: uuid.UUID


class SectionCreateSchema(SectionBaseSchema):
    """Esquema para crear una nueva sección.
    """



class SectionUpdateSchema(SQLModel):
    """Esquema para actualizar una sección. Todos los campos son opcionales.
    """

    title: str | None = None
    image_url: str | None = None
    content: str | None = None
    position_order: int | None = None
    blog_post_id: uuid.UUID | None = None


class SectionReadSchema(SectionBaseSchema):
    """Esquema para leer/devolver datos de una sección desde la API.
    """

    id: uuid.UUID


class SectionReadWithoutBlogPost(SQLModel):
    """Esquema para leer secciones sin incluir el blog_post completo (evita referencias circulares).
    """

    id: uuid.UUID
    title: str
    image_url: str | None = None
    content: str
    position_order: int
