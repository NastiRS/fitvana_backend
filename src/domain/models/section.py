import uuid
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Section(Base, table=True):
    title: str
    image_url: str | None = None
    content: str
    position_order: int = Field(
        default=0, description="Orden de la sección dentro del blog post",
    )

    blog_post_id: uuid.UUID = Field(foreign_key="blogpost.id")
    blog_post: "BlogPost" = Relationship(back_populates="sections")
