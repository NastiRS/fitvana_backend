import uuid
from typing import TypeVar

from sqlmodel import SQLModel

from .base import BaseRepository

ModelType = TypeVar("ModelType", bound=SQLModel)
RelatedModelType = TypeVar("RelatedModelType", bound=SQLModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=SQLModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=SQLModel)


class BaseManyToManyRepository(
    BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType],
):
    """Repositorio base especializado para gestionar relaciones muchos a muchos.
    Extiende el BaseRepository con métodos específicos para gestionar relaciones.
    """

    def add_related_entity(
        self,
        entity_id: uuid.UUID,
        related_entity_id: uuid.UUID,
        related_model: type[RelatedModelType],
        relation_attr: str,
    ) -> ModelType:
        """Método genérico para agregar una entidad relacionada a través de una relación muchos a muchos.

        Args:
            entity_id: ID de la entidad principal
            related_entity_id: ID de la entidad relacionada a agregar
            related_model: Clase del modelo relacionado
            relation_attr: Nombre del atributo de relación en la entidad principal

        Returns:
            La entidad principal actualizada

        Raises:
            ValueError: Si la entidad principal o la relacionada no existen

        """
        entity = self.get_by_id(id=entity_id)
        if not entity:
            raise ValueError(f"{self.model.__name__} con id {entity_id} no encontrado.")

        related_entity = self.session.get(related_model, related_entity_id)
        if not related_entity:
            raise ValueError(
                f"{related_model.__name__} con id {related_entity_id} no encontrado.",
            )

        relation = getattr(entity, relation_attr)

        if related_entity not in relation:
            relation.append(related_entity)
            self.session.add(entity)

        return entity

    def remove_related_entity(
        self,
        entity_id: uuid.UUID,
        related_entity_id: uuid.UUID,
        related_model: type[RelatedModelType],
        relation_attr: str,
    ) -> ModelType:
        """Método genérico para eliminar una entidad relacionada de una relación muchos a muchos.

        Args:
            entity_id: ID de la entidad principal
            related_entity_id: ID de la entidad relacionada a eliminar
            related_model: Clase del modelo relacionado
            relation_attr: Nombre del atributo de relación en la entidad principal

        Returns:
            La entidad principal actualizada

        Raises:
            ValueError: Si la entidad principal o la relacionada no existen

        """
        entity = self.get_by_id(id=entity_id)
        if not entity:
            raise ValueError(f"{self.model.__name__} con id {entity_id} no encontrado.")

        related_entity = self.session.get(related_model, related_entity_id)
        if not related_entity:
            raise ValueError(
                f"{related_model.__name__} con id {related_entity_id} no encontrado.",
            )

        relation = getattr(entity, relation_attr)

        if related_entity in relation:
            relation.remove(related_entity)
            self.session.add(entity)

        return entity

    def get_related_entities(
        self, entity_id: uuid.UUID, relation_attr: str,
    ) -> list[RelatedModelType]:
        """Método genérico para obtener todas las entidades relacionadas.

        Args:
            entity_id: ID de la entidad principal
            relation_attr: Nombre del atributo de relación en la entidad principal

        Returns:
            Lista de entidades relacionadas

        Raises:
            ValueError: Si la entidad principal no existe

        """
        entity = self.get_by_id(id=entity_id)
        if not entity:
            raise ValueError(f"{self.model.__name__} con id {entity_id} no encontrado.")

        return getattr(entity, relation_attr)
