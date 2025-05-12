import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List


from app.repository.blog_post import CurrentBlogPostRepo
from app.domain.schemas.blog_post import (
    BlogPostCreateSchema,
    BlogPostReadSchema,
    BlogPostUpdateSchema,
)

router = APIRouter(prefix="/v1/api/blog_posts", tags=["BlogPosts"])


@router.post("", response_model=BlogPostReadSchema, status_code=status.HTTP_201_CREATED)
def create_blog_post(*, blog_post_in: BlogPostCreateSchema, repo: CurrentBlogPostRepo):
    """
    Crea un nuevo blog post.
    """

    try:
        created_blog_post = repo.create(obj_in=blog_post_in)
        return created_blog_post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear el blog post: {e}",
        )


@router.get("", response_model=List[BlogPostReadSchema])
def read_blog_posts(*, skip: int = 0, limit: int = 100, repo: CurrentBlogPostRepo):
    """
    Obtiene múltiples blog posts con paginación.
    """
    blog_posts = repo.get_all(skip=skip, limit=limit)
    return blog_posts


@router.get("/{blog_post_id}", response_model=BlogPostReadSchema)
def read_blog_post(*, blog_post_id: uuid.UUID, repo: CurrentBlogPostRepo):
    """
    Obtiene un único blog post por su ID.
    """
    db_blog_post = repo.get_by_id(id=blog_post_id)
    if not db_blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="BlogPost no encontrado"
        )
    return db_blog_post


@router.put("/{blog_post_id}", response_model=BlogPostReadSchema)
def update_blog_post(
    *,
    blog_post_id: uuid.UUID,
    blog_post_in: BlogPostUpdateSchema,
    repo: CurrentBlogPostRepo,
):
    """
    Actualiza un blog post existente.
    """
    db_blog_post_to_update = repo.get_by_id(id=blog_post_id)
    if not db_blog_post_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="BlogPost no encontrado"
        )

    try:
        updated_blog_post = repo.update(
            db_obj=db_blog_post_to_update, obj_in=blog_post_in
        )
        return updated_blog_post
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el blog post: {e}",
        )


@router.delete("/{blog_post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog_post(*, blog_post_id: uuid.UUID, repo: CurrentBlogPostRepo):
    """
    Elimina un blog post por su ID.
    """
    db_blog_post = repo.get_by_id(id=blog_post_id)
    if not db_blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="BlogPost no encontrado"
        )
    try:
        repo.delete(entity=db_blog_post)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el blog post: {e}",
        )
    return None
