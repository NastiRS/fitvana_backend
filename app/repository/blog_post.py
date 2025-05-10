from typing import Annotated
from fastapi import Depends
from sqlmodel import Session


from .base import BaseRepository
from app.domain.models.blog_post import BlogPost
from app.core.database.config import get_session


class BlogPostRepository(BaseRepository[BlogPost]):
    """
    Repositorio específico para el modelo BlogPost.
    Hereda la funcionalidad CRUD básica de BaseRepository.
    La sesión de base de datos (db_session) se inyecta a través del constructor de BaseRepository.
    """

    pass


def get_blog_post_repository(
    session: Session = Depends(get_session),
) -> BlogPostRepository:
    return BlogPostRepository(model=BlogPost, db_session=session)


CurrentBlogPostRepo = Annotated[BlogPostRepository, Depends(get_blog_post_repository)]
