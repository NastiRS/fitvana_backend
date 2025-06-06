import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.models.category import Category
from src.domain.schemas.blog_post import BlogPostReadSchema
from src.domain.schemas.category import (
    CategoryCreateSchema,
    CategoryReadSchema,
    CategoryUpdateSchema,
)
from src.repository.blog_post import BlogPostRepository, get_blog_post_repository
from src.repository.category import CurrentCategoryRepo

router = APIRouter(prefix="/v1/api/categories", tags=["Categories"])


@router.post("", response_model=CategoryReadSchema, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreateSchema, repo: CurrentCategoryRepo):
    """Crea una nueva categoría.
    """
    try:
        created_category = repo.create(obj_in=category_in)
        return created_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear la categoría: {e!s}",
        )


@router.get("/{category_id}", response_model=CategoryReadSchema)
def read_category(category_id: uuid.UUID, repo: CurrentCategoryRepo):
    """Obtiene una única categoría por su ID.
    """
    db_category = repo.get_by_id(id=category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada",
        )
    return db_category


@router.get("", response_model=list[CategoryReadSchema])
def read_categories(repo: CurrentCategoryRepo, skip: int = 0, limit: int = 100):
    """Obtiene múltiples categorías con paginación.
    """
    categories = repo.get_all(skip=skip, limit=limit)
    return categories


@router.put("/{category_id}", response_model=CategoryReadSchema)
def update_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdateSchema,
    repo: CurrentCategoryRepo,
):
    """Actualiza una categoría existente.
    """
    db_category_to_update = repo.get_by_id(id=category_id)
    if not db_category_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada",
        )

    try:
        updated_category = repo.update(db_obj=db_category_to_update, obj_in=category_in)
        return updated_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la categoría: {e!s}",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, repo: CurrentCategoryRepo):
    """Elimina una categoría por su ID.
    """
    db_category = repo.get_by_id(id=category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada",
        )
    try:
        repo.delete(entity=db_category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar la categoría: {e!s}",
        )


@router.get("/{category_id}/blog_posts", response_model=list[BlogPostReadSchema])
def get_blog_posts_by_category(
    *,
    category_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository),
):
    """Obtiene todos los blog posts que pertenecen a una categoría específica.
    """
    category = blog_post_repo.session.get(Category, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id {category_id} no encontrada",
        )

    try:
        blog_posts = blog_post_repo.get_blog_posts_by_category(
            category_id=category_id, skip=skip, limit=limit,
        )
        return blog_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener los blog posts de la categoría: {e}",
        )
