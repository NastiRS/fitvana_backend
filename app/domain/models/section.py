import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Section(Base, table=True):
    title: str
    image_url: Optional[str] = None
    content: str

    blog_post_id: uuid.UUID = Field(foreign_key="blogpost.id")
    blog_post: "BlogPost" = Relationship(back_populates="sections")
