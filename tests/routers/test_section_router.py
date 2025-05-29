import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.fixtures import (
    SECTION_BASE_URL,
    SECTION_ID_URL,
    SECTIONS_BY_BLOG_POST_URL,
    create_test_section,
    create_test_blog_post,
)


def test_create_section_success(client: TestClient, db_session_test: Session):
    """
    Test para crear una sección exitosamente.
    """
    blog_post = create_test_blog_post(db_session_test)

    section_data = {
        "title": "Nueva Sección",
        "content": "Contenido de la nueva sección",
        "position_order": 1,
        "image_url": "https://example.com/image.jpg",
        "blog_post_id": str(blog_post.id),
    }

    response = client.post(SECTION_BASE_URL, json=section_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Nueva Sección"
    assert data["content"] == "Contenido de la nueva sección"
    assert data["position_order"] == 1
    assert data["image_url"] == "https://example.com/image.jpg"
    assert data["blog_post_id"] == str(blog_post.id)
    assert "id" in data


def test_create_section_missing_required_fields(client: TestClient):
    """
    Test para verificar que fallan los datos requeridos al crear una sección.
    """
    section_data = {"title": "Sección sin blog_post_id", "content": "Contenido"}

    response = client.post(SECTION_BASE_URL, json=section_data)

    assert response.status_code == 422


def test_read_section_success(client: TestClient, db_session_test: Session):
    """
    Test para obtener una sección por ID exitosamente.
    """
    section = create_test_section(db_session_test)

    response = client.get(SECTION_ID_URL.format(section_id=section.id))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(section.id)
    assert data["title"] == section.title
    assert data["content"] == section.content
    assert data["position_order"] == section.position_order


def test_read_section_not_found(client: TestClient):
    """
    Test para verificar el comportamiento cuando una sección no existe.
    """
    fake_section_id = uuid.uuid4()

    response = client.get(SECTION_ID_URL.format(section_id=fake_section_id))

    assert response.status_code == 404
    assert response.json()["detail"] == "Sección no encontrada"


def test_read_sections_empty(client: TestClient, db_session_test: Session):
    """
    Test para obtener todas las secciones cuando la base de datos está vacía.
    """
    response = client.get(SECTION_BASE_URL)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_read_sections_with_items(client: TestClient, db_session_test: Session):
    """
    Test para obtener todas las secciones cuando hay elementos en la base de datos.
    """
    blog_post = create_test_blog_post(db_session_test)
    _ = create_test_section(
        db_session_test, title="Sección 1", blog_post_id=blog_post.id
    )
    _ = create_test_section(
        db_session_test, title="Sección 2", blog_post_id=blog_post.id
    )

    response = client.get(SECTION_BASE_URL)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    section_titles = [section["title"] for section in data]
    assert "Sección 1" in section_titles
    assert "Sección 2" in section_titles


def test_update_section_success(client: TestClient, db_session_test: Session):
    """
    Test para actualizar una sección exitosamente.
    """
    section = create_test_section(db_session_test)

    update_data = {
        "title": "Sección Actualizada",
        "content": "Contenido actualizado",
        "position_order": 5,
    }

    response = client.put(
        SECTION_ID_URL.format(section_id=section.id), json=update_data
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Sección Actualizada"
    assert data["content"] == "Contenido actualizado"
    assert data["position_order"] == 5
    assert data["id"] == str(section.id)


def test_update_section_not_found(client: TestClient):
    """
    Test para verificar el comportamiento al actualizar una sección que no existe.
    """
    fake_section_id = uuid.uuid4()
    update_data = {"title": "Título Actualizado"}

    response = client.put(
        SECTION_ID_URL.format(section_id=fake_section_id), json=update_data
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Sección no encontrada"


def test_delete_section_success(client: TestClient, db_session_test: Session):
    """
    Test para eliminar una sección exitosamente.
    """
    section = create_test_section(db_session_test)

    response = client.delete(SECTION_ID_URL.format(section_id=section.id))

    assert response.status_code == 204

    # Verificar que la sección ya no existe
    get_response = client.get(SECTION_ID_URL.format(section_id=section.id))
    assert get_response.status_code == 404


def test_delete_section_not_found(client: TestClient):
    """
    Test para verificar el comportamiento al eliminar una sección que no existe.
    """
    fake_section_id = uuid.uuid4()

    response = client.delete(SECTION_ID_URL.format(section_id=fake_section_id))

    assert response.status_code == 404
    assert response.json()["detail"] == "Sección no encontrada"


def test_get_sections_by_blog_post_success(
    client: TestClient, db_session_test: Session
):
    """
    Test para obtener secciones de un blog post específico ordenadas por position_order.
    """
    blog_post = create_test_blog_post(db_session_test)

    # Crear secciones con diferentes position_order
    _ = create_test_section(
        db_session_test, title="Sección 3", position_order=3, blog_post_id=blog_post.id
    )
    _ = create_test_section(
        db_session_test, title="Sección 1", position_order=1, blog_post_id=blog_post.id
    )
    _ = create_test_section(
        db_session_test, title="Sección 2", position_order=2, blog_post_id=blog_post.id
    )

    response = client.get(SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Verificar que están ordenadas por position_order
    assert data[0]["title"] == "Sección 1"
    assert data[0]["position_order"] == 1
    assert data[1]["title"] == "Sección 2"
    assert data[1]["position_order"] == 2
    assert data[2]["title"] == "Sección 3"
    assert data[2]["position_order"] == 3


def test_get_sections_by_blog_post_not_found(client: TestClient):
    """
    Test para verificar el comportamiento cuando el blog post no existe.
    """
    fake_blog_post_id = uuid.uuid4()

    response = client.get(
        SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=fake_blog_post_id)
    )

    assert response.status_code == 404
    assert "Blog post con id" in response.json()["detail"]


def test_get_sections_by_blog_post_empty(client: TestClient, db_session_test: Session):
    """
    Test para obtener secciones de un blog post que no tiene secciones.
    """
    blog_post = create_test_blog_post(db_session_test)

    response = client.get(SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id))

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_sections_by_blog_post_with_pagination(
    client: TestClient, db_session_test: Session
):
    """
    Test para verificar la paginación en la obtención de secciones por blog post.
    """
    blog_post = create_test_blog_post(db_session_test)

    # Crear 5 secciones
    for i in range(1, 6):
        create_test_section(
            db_session_test,
            title=f"Sección {i}",
            position_order=i,
            blog_post_id=blog_post.id,
        )

    # Obtener las primeras 3 secciones
    response = client.get(
        SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id) + "?skip=0&limit=3"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["title"] == "Sección 1"
    assert data[2]["title"] == "Sección 3"

    # Obtener las siguientes 2 secciones
    response = client.get(
        SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id) + "?skip=3&limit=3"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Sección 4"
    assert data[1]["title"] == "Sección 5"


def test_get_sections_by_blog_post_ordered_by_position(
    client: TestClient, db_session_test: Session
):
    """
    Test para verificar que las secciones se devuelven ordenadas por position_order.
    """
    blog_post = create_test_blog_post(db_session_test)

    # Crear secciones con diferentes position_order
    _ = create_test_section(
        db_session_test, title="Sección 3", position_order=3, blog_post_id=blog_post.id
    )
    _ = create_test_section(
        db_session_test, title="Sección 1", position_order=1, blog_post_id=blog_post.id
    )
    _ = create_test_section(
        db_session_test, title="Sección 2", position_order=2, blog_post_id=blog_post.id
    )

    response = client.get(SECTIONS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id))

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Verificar que están ordenadas por position_order
    assert data[0]["title"] == "Sección 1"
    assert data[0]["position_order"] == 1
    assert data[1]["title"] == "Sección 2"
    assert data[1]["position_order"] == 2
    assert data[2]["title"] == "Sección 3"
    assert data[2]["position_order"] == 3
