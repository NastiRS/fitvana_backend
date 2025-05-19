from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.tag import TagReadSchema, TagCreateSchema, TagUpdateSchema
from app.repository.tag import CurrentTagRepo

router = APIRouter(prefix="/v1/api/tags", tags=["Tags"])


@router.post("", response_model=TagReadSchema, status_code=status.HTTP_201_CREATED)
def create_tag(tag_in: TagCreateSchema, repo: CurrentTagRepo):
    """
    Crea un nuevo tag.
    """

    try:
        created_tag = repo.create(obj_in=tag_in)
        return created_tag
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear el tag: {str(e)}",
        )


@router.get("/{tag_id}", response_model=TagReadSchema)
def read_tag(tag_id: uuid.UUID, repo: CurrentTagRepo):
    """
    Obtiene un único tag por su ID.
    """
    db_tag = repo.get_by_id(id=tag_id)
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado"
        )
    return db_tag


@router.get("", response_model=List[TagReadSchema])
def read_tags(repo: CurrentTagRepo, skip: int = 0, limit: int = 100):
    """
    Obtiene múltiples tags con paginación.
    """
    tags = repo.get_all(skip=skip, limit=limit)
    return tags


@router.put("/{tag_id}", response_model=TagReadSchema)
def update_tag(
    tag_id: uuid.UUID,
    tag_in: TagUpdateSchema,
    repo: CurrentTagRepo,
):
    """
    Actualiza un tag existente.
    """
    db_tag_to_update = repo.get_by_id(id=tag_id)
    if not db_tag_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado"
        )

    try:
        updated_tag = repo.update(db_obj=db_tag_to_update, obj_in=tag_in)
        return updated_tag
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el tag: {str(e)}",
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: uuid.UUID, repo: CurrentTagRepo):
    """
    Elimina un tag por su ID.
    """
    db_tag = repo.get_by_id(id=tag_id)
    if not db_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag no encontrado"
        )
    try:
        repo.delete(entity=db_tag)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el tag: {str(e)}",
        )
    return None
