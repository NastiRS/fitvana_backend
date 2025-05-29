from typing import Annotated, List
from fastapi import Depends
from sqlmodel import Session, select
import uuid

from app.repository.base import BaseRepository
from app.domain.models.section import Section
from app.domain.schemas.section import SectionCreateSchema, SectionUpdateSchema
from app.core.database.config import get_session


class SectionRepository(
    BaseRepository[Section, SectionCreateSchema, SectionUpdateSchema]
):
    def __init__(self, model: type, db_session: Session):
        super().__init__(model, db_session)

    def get_sections_by_blog_post(
        self, blog_post_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> List[Section]:
        """
        Obtiene todas las secciones de un blog post específico ordenadas por position_order.
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
