import uuid
from fastapi import APIRouter, HTTPException, status
from typing import List


from app.repository.blog_post import CurrentBlogPostRepo
from app.domain.schemas.blog_post import (
    BlogPostCreateSchema,
    BlogPostReadSchema,
    BlogPostUpdateSchema,
)
from app.domain.schemas.tag import TagReadSchema
from app.domain.schemas.category import CategoryReadSchema

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


@router.post(
    "/{blog_post_id}/tags/{tag_id}",
    response_model=BlogPostReadSchema,
    status_code=status.HTTP_200_OK,
)
def add_tag_to_blog_post(
    *, blog_post_id: uuid.UUID, tag_id: uuid.UUID, repo: CurrentBlogPostRepo
):
    """
    Agrega un tag a un blog post.
    """
    try:
        updated_blog_post = repo.add_tag_to_blog_post(
            blog_post_id=blog_post_id, tag_id=tag_id
        )
        return updated_blog_post
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al agregar el tag al blog post: {e}",
        )


@router.delete(
    "/{blog_post_id}/tags/{tag_id}",
    response_model=BlogPostReadSchema,
    status_code=status.HTTP_200_OK,
)
def remove_tag_from_blog_post(
    *, blog_post_id: uuid.UUID, tag_id: uuid.UUID, repo: CurrentBlogPostRepo
):
    """
    Elimina un tag de un blog post.
    """
    try:
        updated_blog_post = repo.remove_tag_from_blog_post(
            blog_post_id=blog_post_id, tag_id=tag_id
        )
        return updated_blog_post
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el tag del blog post: {e}",
        )


@router.get("/{blog_post_id}/tags", response_model=List[TagReadSchema])
def get_blog_post_tags(*, blog_post_id: uuid.UUID, repo: CurrentBlogPostRepo):
    """
    Obtiene todos los tags asociados a un blog post.
    """
    try:
        tags = repo.get_tags_for_blog_post(blog_post_id=blog_post_id)
        return tags
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener los tags del blog post: {e}",
        )


@router.put("/{blog_post_id}/category/{category_id}", response_model=BlogPostReadSchema)
def assign_category_to_blog_post(
    *, blog_post_id: uuid.UUID, category_id: uuid.UUID, repo: CurrentBlogPostRepo
):
    """
    Asigna una categoría a un blog post.
    """
    try:
        updated_blog_post = repo.assign_category_to_blog_post(
            blog_post_id=blog_post_id, category_id=category_id
        )
        return updated_blog_post
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al asignar la categoría al blog post: {e}",
        )


@router.get("/{blog_post_id}/category", response_model=CategoryReadSchema)
def get_blog_post_category(*, blog_post_id: uuid.UUID, repo: CurrentBlogPostRepo):
    """
    Obtiene la categoría de un blog post.
    """
    try:
        category = repo.get_category_for_blog_post(blog_post_id=blog_post_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El blog post no tiene una categoría asignada",
            )
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener la categoría del blog post: {e}",
        )
