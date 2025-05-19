from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.repository.base import BaseRepository
from app.domain.models.tag import Tag
from app.domain.schemas.tag import TagCreateSchema, TagUpdateSchema
from app.core.database.config import get_session


class TagRepository(BaseRepository[Tag, TagCreateSchema, TagUpdateSchema]):
    def __init__(self, db: Session):
        super().__init__(Tag, db)


def get_tag_repository(session: Session = Depends(get_session)) -> TagRepository:
    return TagRepository(session)


CurrentTagRepo = Annotated[TagRepository, Depends(get_tag_repository)]
