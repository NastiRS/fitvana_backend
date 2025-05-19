import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.domain.models.category import Category

from tests.fixtures import (
    CATEGORY_BASE_URL,
    CATEGORY_ID_URL,
    BLOG_POSTS_BY_CATEGORY_URL,
    create_test_category,
    create_test_blog_post,
)


def test_create_category_success(client: TestClient, db_session_test: Session):
    """Prueba la creación exitosa de una categoría y verifica en BD."""
    category_data = {"name": "Juegos de Mesa", "description": "Diversión analógica"}

    response = client.post(CATEGORY_BASE_URL, json=category_data)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["name"] == category_data["name"]
    assert data["description"] == category_data["description"]
    assert "id" in data
    category_id = data["id"]
    assert uuid.UUID(category_id)

    stmt = select(Category).where(Category.id == uuid.UUID(category_id))
    db_category = db_session_test.exec(stmt).first()
    assert db_category is not None
    assert db_category.name == category_data["name"]
    assert db_category.description == category_data["description"]


def test_create_category_missing_name(client: TestClient):
    """Prueba la creación de una categoría sin el campo 'name' (requerido)."""
    category_data = {"description": "Sin nombre"}
    response = client.post(CATEGORY_BASE_URL, json=category_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_category_success(client: TestClient, db_session_test: Session):
    """Prueba la lectura exitosa de una categoría existente."""
    category_name = "Ropa Deportiva"
    category_desc = "Para atletas"
    new_category = Category(name=category_name, description=category_desc)
    db_session_test.add(new_category)
    db_session_test.commit()
    db_session_test.refresh(new_category)

    created_category_id = new_category.id

    response = client.get(CATEGORY_ID_URL.format(category_id=created_category_id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(created_category_id)
    assert data["name"] == category_name
    assert data["description"] == category_desc


def test_read_category_not_found(client: TestClient):
    """Prueba la lectura de una categoría que no existe."""
    non_existent_id = str(uuid.uuid4())
    response = client.get(CATEGORY_ID_URL.format(category_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_read_categories_empty(client: TestClient, db_session_test: Session):
    """Prueba la lectura de categorías cuando no hay ninguna."""

    all_categories = db_session_test.exec(select(Category)).all()
    for cat in all_categories:
        db_session_test.delete(cat)
    db_session_test.commit()

    response = client.get(CATEGORY_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_read_categories_with_items(client: TestClient, db_session_test: Session):
    """Prueba la lectura de múltiples categorías."""
    cat1 = Category(name="Categoría Test A", description="Desc A")
    cat2 = Category(name="Categoría Test B", description="Desc B")
    db_session_test.add_all([cat1, cat2])
    db_session_test.commit()

    response = client.get(CATEGORY_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    names_from_response = {item["name"] for item in data}
    assert cat1.name in names_from_response
    assert cat2.name in names_from_response


def test_update_category_success(client: TestClient, db_session_test: Session):
    """Prueba la actualización exitosa de una categoría."""
    original_category = Category(
        name="Nombre Original", description="Descripción Original"
    )
    db_session_test.add(original_category)
    db_session_test.commit()
    db_session_test.refresh(original_category)
    category_id_to_update = original_category.id

    update_data = {
        "name": "Nombre Actualizado",
        "description": "Descripción Actualizada",
    }
    response = client.put(
        CATEGORY_ID_URL.format(category_id=category_id_to_update), json=update_data
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(category_id_to_update)
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

    db_session_test.refresh(original_category)
    assert original_category.name == update_data["name"]
    assert original_category.description == update_data["description"]


def test_update_category_not_found(client: TestClient):
    """Prueba la actualización de una categoría que no existe."""
    non_existent_id = str(uuid.uuid4())
    update_data = {"name": "No Importa"}
    response = client.put(
        CATEGORY_ID_URL.format(category_id=non_existent_id), json=update_data
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_category_success(client: TestClient, db_session_test: Session):
    """Prueba la eliminación exitosa de una categoría."""
    category_to_delete = Category(
        name="Para Borrar Definitivamente", description="Adiós"
    )
    db_session_test.add(category_to_delete)
    db_session_test.commit()
    db_session_test.refresh(category_to_delete)
    category_id = category_to_delete.id

    delete_response = client.delete(CATEGORY_ID_URL.format(category_id=category_id))
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    stmt = select(Category).where(Category.id == category_id)
    db_category = db_session_test.exec(stmt).first()
    assert db_category is None

    get_response = client.get(CATEGORY_ID_URL.format(category_id=category_id))
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_category_not_found(client: TestClient):
    """Prueba la eliminación de una categoría que no existe."""
    non_existent_id = str(uuid.uuid4())
    response = client.delete(CATEGORY_ID_URL.format(category_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_blog_posts_by_category_success(
    client: TestClient, db_session_test: Session
):
    """Prueba obtener todos los blog posts de una categoría."""
    category = create_test_category(db_session_test, name="Categoría con Posts")

    post1 = create_test_blog_post(
        db_session_test, title="Post 1 en Categoría", category_id=category.id
    )
    post2 = create_test_blog_post(
        db_session_test, title="Post 2 en Categoría", category_id=category.id
    )

    other_category = create_test_category(db_session_test, name="Otra Categoría")
    create_test_blog_post(
        db_session_test, title="Post en Otra Categoría", category_id=other_category.id
    )

    response = client.get(BLOG_POSTS_BY_CATEGORY_URL.format(category_id=category.id))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2

    post_ids = [post["id"] for post in data]
    assert str(post1.id) in post_ids
    assert str(post2.id) in post_ids

    for post in data:
        assert post["category_id"] == str(category.id)


def test_get_blog_posts_by_category_empty(client: TestClient, db_session_test: Session):
    """Prueba obtener blog posts de una categoría que no tiene ninguno."""
    empty_category = create_test_category(db_session_test, name="Categoría Vacía")

    response = client.get(
        BLOG_POSTS_BY_CATEGORY_URL.format(category_id=empty_category.id)
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_blog_posts_by_category_not_found(client: TestClient):
    """Prueba obtener blog posts de una categoría que no existe."""
    non_existent_id = str(uuid.uuid4())

    response = client.get(
        BLOG_POSTS_BY_CATEGORY_URL.format(category_id=non_existent_id)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrada" in response.json()["detail"]
