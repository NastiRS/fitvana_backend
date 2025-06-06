from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import Base
from .blog_post_tag_link import BlogPostTagLink

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Tag(Base, table=True):
    name: str = Field(index=True, unique=True)

    blog_posts: list["BlogPost"] = Relationship(
        back_populates="tags", link_model=BlogPostTagLink,
    )
