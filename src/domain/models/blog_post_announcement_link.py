import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from .base import Base


class BlogPostAnnouncementLink(Base, table=True):
    blog_post_id: uuid.UUID = Field(
        foreign_key="blogpost.id", primary_key=True, index=True, nullable=False,
    )
    announcement_id: uuid.UUID = Field(
        foreign_key="announcement.id", primary_key=True, index=True, nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "blog_post_id", "announcement_id", name="uq_blog_post_announcement",
        ),
    )
