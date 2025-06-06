from typing import List, TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Category(Base, table=True):
    name: str = Field(index=True)
    description: Optional[str] = None

    blog_posts: List["BlogPost"] = Relationship(back_populates="category")
