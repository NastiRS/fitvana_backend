import uuid
from datetime import date as date_type
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import Base
from .blog_post_announcement_link import BlogPostAnnouncementLink
from .blog_post_tag_link import BlogPostTagLink

if TYPE_CHECKING:
    from .announcement import Announcement
    from .category import Category
    from .section import Section
    from .tag import Tag


class BlogPost(Base, table=True):
    title: str
    content: str
    date: date_type | None = None

    category_id: uuid.UUID = Field(foreign_key="category.id")

    category: "Category" = Relationship(back_populates="blog_posts")
    tags: list["Tag"] = Relationship(
        back_populates="blog_posts", link_model=BlogPostTagLink,
    )
    sections: list["Section"] = Relationship(back_populates="blog_post")
    announcements: list["Announcement"] = Relationship(
        back_populates="blog_posts", link_model=BlogPostAnnouncementLink,
    )
