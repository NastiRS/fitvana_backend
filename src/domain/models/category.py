from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Category(Base, table=True):
    name: str = Field(index=True)
    description: str | None = None

    blog_posts: list["BlogPost"] = Relationship(back_populates="category")
