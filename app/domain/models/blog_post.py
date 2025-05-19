import uuid
from datetime import date as date_type
from typing import List, Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from .base import Base

from .blog_post_tag_link import BlogPostTagLink
from .blog_post_announcement_link import BlogPostAnnouncementLink

if TYPE_CHECKING:
    from .category import Category
    from .tag import Tag
    from .section import Section
    from .announcement import Announcement


class BlogPost(Base, table=True):
    title: str
    content: str
    date: Optional[date_type] = None

    category_id: uuid.UUID = Field(foreign_key="category.id")

    category: "Category" = Relationship(back_populates="blog_posts")
    tags: List["Tag"] = Relationship(
        back_populates="blog_posts", link_model=BlogPostTagLink
    )
    sections: List["Section"] = Relationship(back_populates="blog_post")
    announcements: List["Announcement"] = Relationship(
        back_populates="blog_posts", link_model=BlogPostAnnouncementLink
    )
