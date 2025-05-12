from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from app.repository.base import BaseRepository
from app.domain.models.category import Category
from app.domain.schemas.category import CategoryCreateSchema, CategoryUpdateSchema
from app.core.database.config import get_session


class CategoryRepository(
    BaseRepository[Category, CategoryCreateSchema, CategoryUpdateSchema]
):
    def __init__(self, db: Session):
        super().__init__(Category, db)


def get_category_repository(
    session: Session = Depends(get_session),
) -> CategoryRepository:
    return CategoryRepository(session)


CurrentCategoryRepo = Annotated[CategoryRepository, Depends(get_category_repository)]
