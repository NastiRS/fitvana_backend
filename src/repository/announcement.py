import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from src.core.database.config import get_session
from src.domain.models.announcement import Announcement
from src.domain.models.blog_post import BlogPost
from src.domain.schemas.announcement import (
    AnnouncementCreateSchema,
    AnnouncementUpdateSchema,
)
from src.repository.base_many_to_many import BaseManyToManyRepository


class AnnouncementRepository(
    BaseManyToManyRepository[
        Announcement, AnnouncementCreateSchema, AnnouncementUpdateSchema,
    ],
):
    def __init__(self, model: type, db_session: Session):
        super().__init__(model, db_session)

    def add_announcement_to_blog_post(
        self, blog_post_id: uuid.UUID, announcement_id: uuid.UUID,
    ):
        """Agrega un anuncio a un blog post.
        """
        return self.add_related_entity(
            entity_id=announcement_id,
            related_entity_id=blog_post_id,
            related_model=BlogPost,
            relation_attr="blog_posts",
        )

    def remove_announcement_from_blog_post(
        self, blog_post_id: uuid.UUID, announcement_id: uuid.UUID,
    ):
        """Elimina un anuncio de un blog post.
        """
        return self.remove_related_entity(
            entity_id=announcement_id,
            related_entity_id=blog_post_id,
            related_model=BlogPost,
            relation_attr="blog_posts",
        )

    def get_blog_posts_for_announcement(
        self, announcement_id: uuid.UUID,
    ) -> list[BlogPost]:
        """Obtiene todos los blog posts asociados a un anuncio.
        """
        return self.get_related_entities(
            entity_id=announcement_id, relation_attr="blog_posts",
        )

    def get_announcements_by_blog_post(
        self, blog_post_id: uuid.UUID, skip: int = 0, limit: int = 100,
    ) -> list[Announcement]:
        """Obtiene todos los anuncios asociados a un blog post específico.
        """
        stmt = (
            select(Announcement)
            .join(Announcement.blog_posts)
            .where(BlogPost.id == blog_post_id)
            .offset(skip)
            .limit(limit)
        )
        result = self.session.exec(stmt)
        return list(result.all())


def get_announcement_repository(
    session: Session = Depends(get_session),
) -> AnnouncementRepository:
    return AnnouncementRepository(model=Announcement, db_session=session)


CurrentAnnouncementRepo = Annotated[
    AnnouncementRepository, Depends(get_announcement_repository),
]
