from typing import TYPE_CHECKING, Optional, List

from sqlmodel import Relationship

from .base import Base
from .blog_post_announcement_link import BlogPostAnnouncementLink

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Announcement(Base, table=True):
    name: str
    url: Optional[str] = None
    image_url: Optional[str] = None

    blog_posts: List["BlogPost"] = Relationship(
        back_populates="announcements", link_model=BlogPostAnnouncementLink
    )
