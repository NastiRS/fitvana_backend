import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from src.domain.models.blog_post import BlogPost
from src.domain.schemas.announcement import (
    AnnouncementCreateSchema,
    AnnouncementReadSchema,
    AnnouncementUpdateSchema,
)
from src.domain.schemas.blog_post import BlogPostReadSchema
from src.repository.announcement import CurrentAnnouncementRepo
from src.repository.blog_post import BlogPostRepository, get_blog_post_repository

router = APIRouter(prefix="/v1/api/announcements", tags=["Announcements"])


@router.post(
    "", response_model=AnnouncementReadSchema, status_code=status.HTTP_201_CREATED,
)
def create_announcement(
    announcement_in: AnnouncementCreateSchema, repo: CurrentAnnouncementRepo,
):
    """Crea un nuevo anuncio.
    """
    try:
        created_announcement = repo.create(obj_in=announcement_in)
        return created_announcement
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear el anuncio: {e!s}",
        )


@router.get("/{announcement_id}", response_model=AnnouncementReadSchema)
def read_announcement(announcement_id: uuid.UUID, repo: CurrentAnnouncementRepo):
    """Obtiene un único anuncio por su ID.
    """
    db_announcement = repo.get_by_id(id=announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )
    return db_announcement


@router.get("", response_model=list[AnnouncementReadSchema])
def read_announcements(repo: CurrentAnnouncementRepo, skip: int = 0, limit: int = 100):
    """Obtiene múltiples anuncios con paginación.
    """
    announcements = repo.get_all(skip=skip, limit=limit)
    return announcements


@router.put("/{announcement_id}", response_model=AnnouncementReadSchema)
def update_announcement(
    announcement_id: uuid.UUID,
    announcement_in: AnnouncementUpdateSchema,
    repo: CurrentAnnouncementRepo,
):
    """Actualiza un anuncio existente.
    """
    db_announcement_to_update = repo.get_by_id(id=announcement_id)
    if not db_announcement_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )

    try:
        updated_announcement = repo.update(
            db_obj=db_announcement_to_update, obj_in=announcement_in,
        )
        return updated_announcement
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el anuncio: {e!s}",
        )


@router.delete("/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_announcement(announcement_id: uuid.UUID, repo: CurrentAnnouncementRepo):
    """Elimina un anuncio por su ID.
    """
    db_announcement = repo.get_by_id(id=announcement_id)
    if not db_announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )
    try:
        repo.delete(entity=db_announcement)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el anuncio: {e!s}",
        )


# Endpoints para manejar relaciones muchos a muchos con blog posts


@router.post(
    "/blog_post/{blog_post_id}/announcements/{announcement_id}",
    response_model=AnnouncementReadSchema,
)
def add_announcement_to_blog_post(
    blog_post_id: uuid.UUID,
    announcement_id: uuid.UUID,
    repo: CurrentAnnouncementRepo,
    blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository),
):
    """Agrega un anuncio a un blog post.
    """
    # Verificar que el blog post existe
    blog_post = blog_post_repo.get_by_id(id=blog_post_id)
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post no encontrado",
        )

    # Verificar que el anuncio existe
    announcement = repo.get_by_id(id=announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )

    try:
        updated_announcement = repo.add_announcement_to_blog_post(
            blog_post_id=blog_post_id, announcement_id=announcement_id,
        )
        repo.commit()
        return updated_announcement
    except Exception as e:
        repo.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al agregar el anuncio al blog post: {e!s}",
        )


@router.delete(
    "/blog_post/{blog_post_id}/announcements/{announcement_id}",
    response_model=AnnouncementReadSchema,
)
def remove_announcement_from_blog_post(
    blog_post_id: uuid.UUID,
    announcement_id: uuid.UUID,
    repo: CurrentAnnouncementRepo,
    blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository),
):
    """Elimina un anuncio de un blog post.
    """
    # Verificar que el blog post existe
    blog_post = blog_post_repo.get_by_id(id=blog_post_id)
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Blog post no encontrado",
        )

    # Verificar que el anuncio existe
    announcement = repo.get_by_id(id=announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )

    try:
        updated_announcement = repo.remove_announcement_from_blog_post(
            blog_post_id=blog_post_id, announcement_id=announcement_id,
        )
        repo.commit()
        return updated_announcement
    except Exception as e:
        repo.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el anuncio del blog post: {e!s}",
        )


@router.get("/{announcement_id}/blog_posts", response_model=list[BlogPostReadSchema])
def get_blog_posts_for_announcement(
    announcement_id: uuid.UUID,
    repo: CurrentAnnouncementRepo,
):
    """Obtiene todos los blog posts asociados a un anuncio.
    """
    announcement = repo.get_by_id(id=announcement_id)
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Anuncio no encontrado",
        )

    try:
        blog_posts = repo.get_blog_posts_for_announcement(
            announcement_id=announcement_id,
        )
        return blog_posts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener los blog posts del anuncio: {e!s}",
        )


@router.get("/blog_post/{blog_post_id}", response_model=list[AnnouncementReadSchema])
def get_announcements_by_blog_post(
    *,
    blog_post_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    repo: CurrentAnnouncementRepo,
    blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository),
):
    """Obtiene todos los anuncios asociados a un blog post específico.
    """
    blog_post = blog_post_repo.session.get(BlogPost, blog_post_id)
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post con id {blog_post_id} no encontrado",
        )

    try:
        announcements = repo.get_announcements_by_blog_post(
            blog_post_id=blog_post_id, skip=skip, limit=limit,
        )
        return announcements
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener los anuncios del blog post: {e}",
        )
