from typing import TYPE_CHECKING

from sqlmodel import Relationship

from .base import Base
from .blog_post_announcement_link import BlogPostAnnouncementLink

if TYPE_CHECKING:
    from .blog_post import BlogPost


class Announcement(Base, table=True):
    name: str
    url: str | None = None
    image_url: str | None = None

    blog_posts: list["BlogPost"] = Relationship(
        back_populates="announcements", link_model=BlogPostAnnouncementLink,
    )
