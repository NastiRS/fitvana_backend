from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from sqlmodel import SQLModel, Session, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db_session: Session):
        """
        Repositorio base con operaciones fundamentales de acceso a datos.
        Este repositorio espera que la gestión de transacciones (commit, rollback)
        sea manejada por la capa que lo utiliza.

        **Parámetros**

        * `model`: Una clase de modelo SQLModel.
        * `db_session`: La sesión de base de datos SQLModel/SQLAlchemy.
        """
        self.model = model
        self.session = db_session

    def _save(self, entity: ModelType) -> None:
        """
        Persiste el estado actual de la entidad en la base de datos y la refresca.
        Llama a flush para enviar los cambios a la BD y refresh para actualizar la entidad.
        Si ocurre un error, la excepción se propaga para ser manejada por el método llamador.
        """
        self.session.flush()
        self.session.refresh(entity)

    def create(self, *, entity_in: ModelType) -> ModelType:
        """
        Añade una nueva entidad a la sesión y la guarda.
        Si ocurre un error, se realiza un rollback de la sesión y se relanza la excepción.
        El llamador es responsable de hacer commit si la operación es exitosa.
        """
        try:
            self.session.add(entity_in)
            self._save(entity_in)
            return entity_in
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, id: Any) -> Optional[ModelType]:
        """
        Obtiene un único registro por su ID. Retorna None si no se encuentra.
        Asume que el campo de la clave primaria se llama 'id'.
        """
        statement = select(self.model).where(getattr(self.model, "id") == id)
        return self.session.exec(statement).first()

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Obtiene múltiples registros con paginación y filtrado opcionales.
        La ordenación ha sido eliminada.

        **Parámetros para filtrado (filters)**:
        Un diccionario donde la clave es el nombre del campo y el valor es el valor a filtrar (igualdad exacta).
        Ejemplo: `filters={"nombre": "Ejemplo", "activo": True}`
        """
        statement = select(self.model)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field):
                    statement = statement.where(getattr(self.model, field) == value)
                else:
                    raise ValueError(
                        f"Campo de filtro inválido: '{field}' no existe en el modelo {self.model.__name__}."
                    )

        statement = statement.offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update(self, *, entity: ModelType) -> ModelType:
        """
        Guarda los cambios de una entidad existente.
        Se asume que la entidad ya está asociada a la sesión y ha sido modificada.
        El llamador es responsable de hacer commit.
        """
        try:
            self.session.add(entity)
            self._save(entity)
            return entity
        except Exception:
            self.session.rollback()
            raise

    def delete(self, *, entity: ModelType) -> None:
        """
        Elimina una entidad de la sesión.
        Si ocurre un error (ej. violación de FK durante el flush),
        se realiza un rollback y se relanza la excepción.
        El llamador es responsable de hacer commit si la operación es exitosa.
        """
        try:
            self.session.delete(entity)
            self.session.flush()
        except Exception:
            self.session.rollback()
            raise

    def commit(self) -> None:
        """Confirma la transacción actual."""
        self.session.commit()

    def rollback(self) -> None:
        """Revierte la transacción actual."""
        self.session.rollback()

    def flush(self) -> None:
        """
        Sincroniza los cambios de la sesión con la base de datos sin hacer commit.
        Útil para obtener IDs generados por la BD antes del commit final.
        """
        self.session.flush()
