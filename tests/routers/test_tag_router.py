import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.domain.models.tag import Tag
from tests.fixtures import TAG_BASE_URL, TAG_ID_URL


def test_create_tag_success(client: TestClient, db_session_test: Session):
    """Prueba la creación exitosa de un tag y verifica en BD."""
    tag_data = {"name": "Python Test"}
    response = client.post(TAG_BASE_URL, json=tag_data)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == tag_data["name"]
    assert "id" in data
    tag_id = data["id"]
    assert uuid.UUID(tag_id)

    stmt = select(Tag).where(Tag.id == uuid.UUID(tag_id))
    db_tag = db_session_test.exec(stmt).first()
    assert db_tag is not None
    assert db_tag.name == tag_data["name"]


def test_create_tag_missing_name(client: TestClient):
    """Prueba la creación de un tag sin el campo 'name' (requerido)."""
    tag_data = {}
    response = client.post(TAG_BASE_URL, json=tag_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_tag_success(client: TestClient, db_session_test: Session):
    """Prueba la lectura exitosa de un tag existente."""
    tag_name = "FastAPI Test"
    new_tag = Tag(name=tag_name)
    db_session_test.add(new_tag)
    db_session_test.commit()
    db_session_test.refresh(new_tag)
    created_tag_id = new_tag.id

    response = client.get(TAG_ID_URL.format(tag_id=created_tag_id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(created_tag_id)
    assert data["name"] == tag_name


def test_read_tag_not_found(client: TestClient):
    """Prueba la lectura de un tag que no existe."""
    non_existent_id = str(uuid.uuid4())
    response = client.get(TAG_ID_URL.format(tag_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Tag no encontrado"


def test_read_tags_empty(client: TestClient, db_session_test: Session):
    """Prueba la lectura de tags cuando no hay ninguno."""
    all_tags = db_session_test.exec(select(Tag)).all()
    for t in all_tags:
        db_session_test.delete(t)
    db_session_test.commit()

    response = client.get(TAG_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_read_tags_with_items(client: TestClient, db_session_test: Session):
    """Prueba la lectura de múltiples tags."""
    tag1 = Tag(name="Tag Test X")
    tag2 = Tag(name="Tag Test Y")
    db_session_test.add_all([tag1, tag2])
    db_session_test.commit()

    response = client.get(TAG_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    names_from_response = {item["name"] for item in data}
    assert tag1.name in names_from_response
    assert tag2.name in names_from_response


def test_update_tag_success(client: TestClient, db_session_test: Session):
    """Prueba la actualización exitosa de un tag."""
    original_tag = Tag(name="Nombre Original Tag")
    db_session_test.add(original_tag)
    db_session_test.commit()
    db_session_test.refresh(original_tag)
    tag_id_to_update = original_tag.id

    update_data = {"name": "Nombre Tag Actualizado"}
    response = client.put(TAG_ID_URL.format(tag_id=tag_id_to_update), json=update_data)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(tag_id_to_update)
    assert data["name"] == update_data["name"]

    db_session_test.refresh(original_tag)
    assert original_tag.name == update_data["name"]


def test_update_tag_not_found(client: TestClient):
    """Prueba la actualización de un tag que no existe."""
    non_existent_id = str(uuid.uuid4())
    update_data = {"name": "No Importa Tag"}
    response = client.put(TAG_ID_URL.format(tag_id=non_existent_id), json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_tag_success(client: TestClient, db_session_test: Session):
    """Prueba la eliminación exitosa de un tag."""
    tag_to_delete = Tag(name="Tag Para Eliminar Ya")
    db_session_test.add(tag_to_delete)
    db_session_test.commit()
    db_session_test.refresh(tag_to_delete)
    tag_id = tag_to_delete.id

    delete_response = client.delete(TAG_ID_URL.format(tag_id=tag_id))
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    stmt = select(Tag).where(Tag.id == tag_id)
    db_tag = db_session_test.exec(stmt).first()
    assert db_tag is None

    get_response = client.get(TAG_ID_URL.format(tag_id=tag_id))
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_tag_not_found(client: TestClient):
    """Prueba la eliminación de un tag que no existe."""
    non_existent_id = str(uuid.uuid4())
    response = client.delete(TAG_ID_URL.format(tag_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
