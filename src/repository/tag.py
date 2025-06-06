from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from src.core.database.config import get_session
from src.domain.models.tag import Tag
from src.domain.schemas.tag import TagCreateSchema, TagUpdateSchema
from src.repository.base import BaseRepository


class TagRepository(BaseRepository[Tag, TagCreateSchema, TagUpdateSchema]):
    def __init__(self, model: type, db_session: Session):
        super().__init__(model, db_session)


def get_tag_repository(session: Session = Depends(get_session)) -> TagRepository:
    return TagRepository(model=Tag, db_session=session)


CurrentTagRepo = Annotated[TagRepository, Depends(get_tag_repository)]
