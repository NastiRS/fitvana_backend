from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.category import (
    CategoryReadSchema,
    CategoryCreateSchema,
    CategoryUpdateSchema,
)
from app.repository.category import CurrentCategoryRepo

router = APIRouter(prefix="/v1/api/category", tags=["Categories"])


@router.post("", response_model=CategoryReadSchema, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreateSchema, repo: CurrentCategoryRepo):
    """
    Crea una nueva categoría.
    """

    try:
        created_category = repo.create(obj_in=category_in)
        return created_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear la categoría: {str(e)}",
        )


@router.get("/{category_id}", response_model=CategoryReadSchema)
def read_category(category_id: uuid.UUID, repo: CurrentCategoryRepo):
    """
    Obtiene una única categoría por su ID.
    """
    db_category = repo.get_by_id(id=category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return db_category


@router.get("", response_model=List[CategoryReadSchema])
def read_categories(repo: CurrentCategoryRepo, skip: int = 0, limit: int = 100):
    """
    Obtiene múltiples categorías con paginación.
    """
    categories = repo.get_all(skip=skip, limit=limit)
    return categories


@router.put("/{category_id}", response_model=CategoryReadSchema)
def update_category(
    category_id: uuid.UUID,
    category_in: CategoryUpdateSchema,
    repo: CurrentCategoryRepo,
):
    """
    Actualiza una categoría existente.
    """
    db_category_to_update = repo.get_by_id(id=category_id)
    if not db_category_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )

    try:
        updated_category = repo.update(db_obj=db_category_to_update, obj_in=category_in)
        return updated_category
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la categoría: {str(e)}",
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: uuid.UUID, repo: CurrentCategoryRepo):
    """
    Elimina una categoría por su ID.
    """
    db_category = repo.get_by_id(id=category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    try:
        repo.delete(entity=db_category)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar la categoría: {str(e)}",
        )
    return None
