import uuid

from sqlmodel import Field
from sqlalchemy import UniqueConstraint

from .base import Base


class BlogPostTagLink(Base, table=True):
    blog_post_id: uuid.UUID = Field(
        foreign_key="blogpost.id", primary_key=True, index=True, nullable=False
    )
    tag_id: uuid.UUID = Field(
        foreign_key="tag.id", primary_key=True, index=True, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("blog_post_id", "tag_id", name="uq_blog_post_tag"),
    )
