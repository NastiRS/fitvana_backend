import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, select

from src.core.database.config import get_session
from src.domain.models.blog_post import BlogPost
from src.domain.models.category import Category
from src.domain.models.tag import Tag
from src.domain.schemas.blog_post import BlogPostCreateSchema, BlogPostUpdateSchema

from .base_many_to_many import BaseManyToManyRepository


class BlogPostRepository(
    BaseManyToManyRepository[BlogPost, BlogPostCreateSchema, BlogPostUpdateSchema],
):
    """Repositorio específico para el modelo BlogPost.
    Hereda la funcionalidad CRUD básica de BaseRepository y la funcionalidad
    de relaciones muchos a muchos de BaseManyToManyRepository.
    La sesión de base de datos (session) se inyecta a través del constructor de BaseRepository.
    """

    def add_tag_to_blog_post(self, blog_post_id: uuid.UUID, tag_id: uuid.UUID):
        """Agrega un tag a un blog post.
        """
        return self.add_related_entity(
            entity_id=blog_post_id,
            related_entity_id=tag_id,
            related_model=Tag,
            relation_attr="tags",
        )

    def remove_tag_from_blog_post(self, blog_post_id: uuid.UUID, tag_id: uuid.UUID):
        """Elimina un tag de un blog post.
        """
        return self.remove_related_entity(
            entity_id=blog_post_id,
            related_entity_id=tag_id,
            related_model=Tag,
            relation_attr="tags",
        )

    def get_tags_for_blog_post(self, blog_post_id: uuid.UUID) -> list[Tag]:
        """Obtiene todos los tags asociados a un blog post.
        """
        return self.get_related_entities(entity_id=blog_post_id, relation_attr="tags")

    def assign_category_to_blog_post(
        self, blog_post_id: uuid.UUID, category_id: uuid.UUID,
    ) -> BlogPost:
        """Asigna una categoría a un blog post.

        Args:
            blog_post_id: ID del blog post
            category_id: ID de la categoría a asignar

        Returns:
            El blog post actualizado

        Raises:
            ValueError: Si el blog post o la categoría no existen

        """
        blog_post = self.get_by_id(id=blog_post_id)
        if not blog_post:
            raise ValueError(f"BlogPost con id {blog_post_id} no encontrado.")

        category = self.session.get(Category, category_id)
        if not category:
            raise ValueError(f"Category con id {category_id} no encontrada.")

        blog_post.category_id = category_id
        blog_post.category = category

        self.session.add(blog_post)

        return blog_post

    def get_category_for_blog_post(self, blog_post_id: uuid.UUID) -> Category | None:
        """Obtiene la categoría asociada a un blog post.

        Args:
            blog_post_id: ID del blog post

        Returns:
            La categoría asociada al blog post o None si no tiene categoría

        Raises:
            ValueError: Si el blog post no existe

        """
        blog_post = self.get_by_id(id=blog_post_id)
        if not blog_post:
            raise ValueError(f"BlogPost con id {blog_post_id} no encontrado.")

        return blog_post.category

    def get_blog_posts_by_category(
        self, category_id: uuid.UUID, skip: int = 0, limit: int = 100,
    ) -> list[BlogPost]:
        """Obtiene todos los blog posts pertenecientes a una categoría.

        Args:
            category_id: ID de la categoría
            skip: Número de registros a saltar (para paginación)
            limit: Límite de registros a devolver (para paginación)

        Returns:
            Lista de blog posts que pertenecen a la categoría

        """
        statement = (
            select(BlogPost)
            .where(BlogPost.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return self.session.exec(statement).all()


def get_blog_post_repository(
    session: Session = Depends(get_session),
) -> BlogPostRepository:
    return BlogPostRepository(model=BlogPost, db_session=session)


CurrentBlogPostRepo = Annotated[BlogPostRepository, Depends(get_blog_post_repository)]
