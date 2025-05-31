from typing import List
import uuid
from fastapi import APIRouter, HTTPException, status

from app.domain.schemas.user import (
    UserReadSchema,
    UserCreateSchema,
    UserUpdateSchema,
    UserUpdatePasswordSchema,
    UserAcceptTermsSchema,
    UserReadPublicSchema,
    UserRoleUpdateSchema,
    UserLanguageUpdateSchema,
    UserCurrencyUpdateSchema,
)
from app.repository.user import CurrentUserRepo
from app.domain.models.user import UserRole
from app.auth.dependencies import CurrentActiveUser
from app.auth.password import password_manager

router = APIRouter(prefix="/v1/api/users", tags=["Users"])


@router.post("", response_model=UserReadSchema, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreateSchema, repo: CurrentUserRepo, current_user: CurrentActiveUser
):
    """
    Crea un nuevo usuario (solo admin).
    Nota: Para registro público, usar /auth/register
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    # Verificar si el email ya existe
    existing_user = repo.get_by_email(email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email",
        )

    # Verificar si el username ya existe (si se proporciona)
    if user_in.username:
        existing_username = repo.get_by_username(username=user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este username",
            )

    try:
        # Hashear la contraseña antes de crear el usuario
        hashed_password = password_manager.get_password_hash(user_in.password)

        # Crear datos del usuario con contraseña hasheada
        user_dict = user_in.model_dump()
        user_dict.pop("password")  # Remover contraseña en texto plano
        user_dict["hashed_password"] = hashed_password

        created_user = repo.create_from_dict(obj_dict=user_dict)
        return created_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al crear el usuario: {str(e)}",
        )


@router.get("/{user_id}", response_model=UserReadSchema)
def read_user(
    user_id: uuid.UUID, repo: CurrentUserRepo, current_user: CurrentActiveUser
):
    """
    Obtiene un único usuario por su ID.
    Los usuarios pueden ver su propio perfil, admin puede ver cualquiera.
    """
    # Verificar que el usuario puede acceder a esta información
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este usuario",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return db_user


@router.get("/{user_id}/public", response_model=UserReadPublicSchema)
def read_user_public_profile(user_id: uuid.UUID, repo: CurrentUserRepo):
    """
    Obtiene el perfil público de un usuario.
    No requiere autenticación.
    """
    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    return db_user


@router.get("", response_model=List[UserReadSchema])
def read_users(
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene múltiples usuarios con paginación.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    users = repo.get_all(skip=skip, limit=limit)
    return users


@router.get("/active", response_model=List[UserReadSchema])
def read_active_users(
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene todos los usuarios activos.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    users = repo.get_active_users(skip=skip, limit=limit)
    return users


@router.get("/role/{role}", response_model=List[UserReadSchema])
def read_users_by_role(
    role: str,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene usuarios por rol específico.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    users = repo.get_users_by_role(role=role, skip=skip, limit=limit)
    return users


@router.get("/unverified", response_model=List[UserReadSchema])
def read_unverified_users(
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
    skip: int = 0,
    limit: int = 100,
):
    """
    Obtiene usuarios no verificados.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    users = repo.get_unverified_users(skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=UserReadSchema)
def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdateSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza un usuario existente.
    Los usuarios pueden actualizar su propio perfil, admin puede actualizar cualquiera.
    """
    # Verificar permisos
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar este usuario",
        )

    db_user_to_update = repo.get_by_id(id=user_id)
    if not db_user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Verificar email único si se está actualizando
    if user_in.email and user_in.email != db_user_to_update.email:
        existing_user = repo.get_by_email(email=user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este email",
            )

    # Verificar username único si se está actualizando
    if user_in.username and user_in.username != db_user_to_update.username:
        existing_username = repo.get_by_username(username=user_in.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con este username",
            )

    try:
        updated_user = repo.update(db_obj=db_user_to_update, obj_in=user_in)
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el usuario: {str(e)}",
        )


@router.put("/{user_id}/role", response_model=UserReadSchema)
def update_user_role(
    user_id: uuid.UUID,
    role_data: UserRoleUpdateSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza el rol de un usuario.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    try:
        db_user.role = role_data.role
        updated_user = repo.update(db_obj=db_user, obj_in={})
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el rol: {str(e)}",
        )


@router.put("/{user_id}/password", response_model=UserReadSchema)
def update_user_password(
    user_id: uuid.UUID,
    password_data: UserUpdatePasswordSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza la contraseña de un usuario.
    Los usuarios pueden cambiar su propia contraseña, admin puede cambiar cualquiera.
    Nota: Para cambio de contraseña autenticado, usar /auth/change-password
    """
    # Verificar permisos
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar la contraseña de este usuario",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    # Verificar contraseña actual
    if not password_manager.verify_password(
        password_data.current_password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta",
        )

    try:
        # Hashear la nueva contraseña
        hashed_new_password = password_manager.get_password_hash(
            password_data.new_password
        )
        db_user.hashed_password = hashed_new_password

        repo.update_password_reset_request(user=db_user)
        return db_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la contraseña: {str(e)}",
        )


@router.put("/{user_id}/verify", response_model=UserReadSchema)
def verify_user(
    user_id: uuid.UUID, repo: CurrentUserRepo, current_user: CurrentActiveUser
):
    """
    Marca un usuario como verificado.
    Solo accesible para administradores.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    try:
        verified_user = repo.verify_user(user=db_user)
        return verified_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al verificar el usuario: {str(e)}",
        )


@router.put("/{user_id}/accept-terms", response_model=UserReadSchema)
def accept_terms(
    user_id: uuid.UUID,
    terms_data: UserAcceptTermsSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza la aceptación de términos y políticas de un usuario.
    Los usuarios solo pueden actualizar sus propios términos.
    """
    # Verificar permisos
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes actualizar tus propios términos",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    try:
        updated_user = repo.accept_terms(
            user=db_user,
            accept_terms=terms_data.accept_terms,
            accept_privacy=terms_data.accept_privacy_policy,
        )
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la aceptación de términos: {str(e)}",
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID, repo: CurrentUserRepo, current_user: CurrentActiveUser
):
    """
    Elimina un usuario por su ID.
    Los usuarios pueden eliminar su propia cuenta, admin puede eliminar cualquier cuenta.
    """
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para eliminar este usuario",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )
    try:
        repo.delete(entity=db_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al eliminar el usuario: {str(e)}",
        )
    return None


@router.put("/{user_id}/language", response_model=UserReadSchema)
def update_user_language(
    user_id: uuid.UUID,
    language_data: UserLanguageUpdateSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza el idioma preferido de un usuario.
    Los usuarios pueden cambiar su propio idioma, admin puede cambiar cualquiera.
    """
    # Verificar permisos
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar el idioma de este usuario",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    try:
        db_user.language = language_data.language
        updated_user = repo.update(db_obj=db_user, obj_in={})
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar el idioma: {str(e)}",
        )


@router.put("/{user_id}/currency", response_model=UserReadSchema)
def update_user_currency(
    user_id: uuid.UUID,
    currency_data: UserCurrencyUpdateSchema,
    repo: CurrentUserRepo,
    current_user: CurrentActiveUser,
):
    """
    Actualiza la moneda preferida de un usuario.
    Los usuarios pueden cambiar su propia moneda, admin puede cambiar cualquiera.
    """
    # Verificar permisos
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar la moneda de este usuario",
        )

    db_user = repo.get_by_id(id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
        )

    try:
        db_user.currency_preference = currency_data.currency_preference
        updated_user = repo.update(db_obj=db_user, obj_in={})
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al actualizar la moneda: {str(e)}",
        )
