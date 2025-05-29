from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status, Depends

from app.domain.schemas.section import (
    SectionReadSchema,
    SectionCreateSchema,
    SectionUpdateSchema,
)
from app.repository.section import CurrentSectionRepo
from app.repository.blog_post import BlogPostRepository, get_blog_post_repository
from app.domain.models.blog_post import BlogPost

router = APIRouter(prefix="/v1/api/sections", tags=["Sections"])


@router.post("", response_model=SectionReadSchema, status_code=status.HTTP_201_CREATED)
def create_section(section_in: SectionCreateSchema, repo: CurrentSectionRepo):
    """
    Crea una nueva sección.
    """

    try:
        created_section = repo.create(obj_in=section_in)
        return created_section
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear la sección: {str(e)}",
        )


@router.get("/{section_id}", response_model=SectionReadSchema)
def read_section(section_id: uuid.UUID, repo: CurrentSectionRepo):
    """
    Obtiene una única sección por su ID.
    """
    db_section = repo.get_by_id(id=section_id)
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
        )
    return db_section


@router.get("", response_model=List[SectionReadSchema])
def read_sections(repo: CurrentSectionRepo, skip: int = 0, limit: int = 100):
    """
    Obtiene múltiples secciones con paginación.
    """
    sections = repo.get_all(skip=skip, limit=limit)
    return sections


@router.put("/{section_id}", response_model=SectionReadSchema)
def update_section(
    section_id: uuid.UUID,
    section_in: SectionUpdateSchema,
    repo: CurrentSectionRepo,
):
    """
    Actualiza una sección existente.
    """
    db_section_to_update = repo.get_by_id(id=section_id)
    if not db_section_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
        )

    try:
        updated_section = repo.update(db_obj=db_section_to_update, obj_in=section_in)
        return updated_section
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la sección: {str(e)}",
        )


@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_section(section_id: uuid.UUID, repo: CurrentSectionRepo):
    """
    Elimina una sección por su ID.
    """
    db_section = repo.get_by_id(id=section_id)
    if not db_section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Sección no encontrada"
        )
    try:
        repo.delete(entity=db_section)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar la sección: {str(e)}",
        )
    return None


@router.get("/blog_post/{blog_post_id}", response_model=List[SectionReadSchema])
def get_sections_by_blog_post(
    *,
    blog_post_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    repo: CurrentSectionRepo,
    blog_post_repo: BlogPostRepository = Depends(get_blog_post_repository),
):
    """
    Obtiene todas las secciones que pertenecen a un blog post específico ordenadas por position_order.
    """
    blog_post = blog_post_repo.session.get(BlogPost, blog_post_id)
    if not blog_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog post con id {blog_post_id} no encontrado",
        )

    try:
        sections = repo.get_sections_by_blog_post(
            blog_post_id=blog_post_id, skip=skip, limit=limit
        )
        return sections
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al obtener las secciones del blog post: {e}",
        )
