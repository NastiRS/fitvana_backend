import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from src.core.database.config import get_session
from src.domain.models.section import Section
from src.domain.schemas.section import SectionCreateSchema, SectionUpdateSchema
from src.repository.base import BaseRepository


class SectionRepository(
    BaseRepository[Section, SectionCreateSchema, SectionUpdateSchema],
):
    def __init__(self, model: type, db_session: Session):
        super().__init__(model, db_session)

    def get_sections_by_blog_post(
        self, blog_post_id: uuid.UUID, skip: int = 0, limit: int = 100,
    ) -> list[Section]:
        """Obtiene todas las secciones de un blog post específico ordenadas por position_order.
        """
        stmt = (
            select(Section)
            .where(Section.blog_post_id == blog_post_id)
            .order_by(Section.position_order)
            .offset(skip)
            .limit(limit)
        )
        result = self.session.exec(stmt)
        return list(result.all())


def get_section_repository(
    session: Session = Depends(get_session),
) -> SectionRepository:
    return SectionRepository(model=Section, db_session=session)


CurrentSectionRepo = Annotated[SectionRepository, Depends(get_section_repository)]
