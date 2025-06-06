from typing import Any, Generic, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], db_session: Session):
        """Repositorio base con operaciones fundamentales de acceso a datos.
        Este repositorio espera que la gestión de transacciones (commit, rollback)
        sea manejada por la capa que lo utiliza.

        **Parámetros**

        * `model`: Una clase de modelo SQLModel.
        * `db_session`: La sesión de base de datos SQLModel/SQLAlchemy.
        """
        self.model = model
        self.session = db_session

    def _save(self, entity: ModelType) -> None:
        """Persiste el estado actual de la entidad en la base de datos y la refresca.
        Llama a flush para enviar los cambios a la BD y refresh para actualizar la entidad.
        Si ocurre un error, la excepción se propaga para ser manejada por el método llamador.
        """
        self.session.flush()
        self.session.refresh(entity)

    def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Crea un nuevo registro en la base de datos.
        Convierte el schema de creación al modelo antes de guardarlo.
        """
        db_obj = self.model.model_validate(obj_in)
        try:
            self.session.add(db_obj)
            self._save(db_obj)
            return db_obj
        except Exception:
            self.session.rollback()
            raise

    def create_from_dict(self, *, obj_dict: dict[str, Any]) -> ModelType:
        """Crea un nuevo registro en la base de datos a partir de un diccionario.
        Útil cuando se necesitan realizar transformaciones antes de la creación,
        como hashear contraseñas.
        """
        db_obj = self.model(**obj_dict)
        try:
            self.session.add(db_obj)
            self._save(db_obj)
            return db_obj
        except Exception:
            self.session.rollback()
            raise

    def get_by_id(self, id: Any) -> ModelType | None:
        """Obtiene un único registro por su ID. Retorna None si no se encuentra.
        Asume que el campo de la clave primaria se llama 'id'.
        """
        statement = select(self.model).where(self.model.id == id)
        return self.session.exec(statement).first()

    def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: dict[str, Any] | None = None,
    ) -> list[ModelType]:
        """Obtiene múltiples registros con paginación y filtrado opcionales.
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
                        f"Campo de filtro inválido: '{field}' no existe en el modelo {self.model.__name__}.",
                    )

        statement = statement.offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def update(self, *, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """Actualiza un registro existente en la base de datos.
        """
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)

        try:
            self.session.add(db_obj)
            self._save(db_obj)
            return db_obj
        except Exception:
            self.session.rollback()
            raise

    def delete(self, *, entity: ModelType) -> None:
        """Elimina una entidad de la sesión.
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
        """Sincroniza los cambios de la sesión con la base de datos sin hacer commit.
        Útil para obtener IDs generados por la BD antes del commit final.
        """
        self.session.flush()
