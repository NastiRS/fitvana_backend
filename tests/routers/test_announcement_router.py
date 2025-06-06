import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.fixtures import (
    ANNOUNCEMENT_BASE_URL,
    ANNOUNCEMENT_BLOG_POSTS_URL,
    ANNOUNCEMENT_ID_URL,
    ANNOUNCEMENT_TO_BLOG_POST_URL,
    ANNOUNCEMENTS_BY_BLOG_POST_URL,
    create_test_announcement,
    create_test_blog_post,
)


def test_create_announcement_success(client: TestClient, db_session_test: Session):
    """Test para crear un anuncio exitosamente.
    """
    announcement_data = {
        "name": "Nuevo Anuncio",
        "url": "https://ejemplo.com",
        "image_url": "https://ejemplo.com/imagen.jpg",
    }

    response = client.post(ANNOUNCEMENT_BASE_URL, json=announcement_data)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Nuevo Anuncio"
    assert data["url"] == "https://ejemplo.com"
    assert data["image_url"] == "https://ejemplo.com/imagen.jpg"
    assert "id" in data


def test_create_announcement_missing_required_fields(client: TestClient):
    """Test para verificar que fallan los datos requeridos al crear un anuncio.
    """
    announcement_data = {"url": "https://ejemplo.com"}

    response = client.post(ANNOUNCEMENT_BASE_URL, json=announcement_data)

    assert response.status_code == 422


def test_read_announcement_success(client: TestClient, db_session_test: Session):
    """Test para obtener un anuncio por ID exitosamente.
    """
    announcement = create_test_announcement(db_session_test)

    response = client.get(ANNOUNCEMENT_ID_URL.format(announcement_id=announcement.id))

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(announcement.id)
    assert data["name"] == announcement.name
    assert data["url"] == announcement.url
    assert data["image_url"] == announcement.image_url


def test_read_announcement_not_found(client: TestClient):
    """Test para verificar el comportamiento cuando un anuncio no existe.
    """
    fake_announcement_id = uuid.uuid4()

    response = client.get(
        ANNOUNCEMENT_ID_URL.format(announcement_id=fake_announcement_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anuncio no encontrado"


def test_read_announcements_empty(client: TestClient, db_session_test: Session):
    """Test para obtener todos los anuncios cuando la base de datos está vacía.
    """
    response = client.get(ANNOUNCEMENT_BASE_URL)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_read_announcements_with_items(client: TestClient, db_session_test: Session):
    """Test para obtener todos los anuncios cuando hay elementos en la base de datos.
    """
    _ = create_test_announcement(db_session_test, name="Anuncio 1")
    _ = create_test_announcement(db_session_test, name="Anuncio 2")

    response = client.get(ANNOUNCEMENT_BASE_URL)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    announcement_names = [announcement["name"] for announcement in data]
    assert "Anuncio 1" in announcement_names
    assert "Anuncio 2" in announcement_names


def test_update_announcement_success(client: TestClient, db_session_test: Session):
    """Test para actualizar un anuncio exitosamente.
    """
    announcement = create_test_announcement(db_session_test)

    update_data = {
        "name": "Anuncio Actualizado",
        "url": "https://actualizado.com",
        "image_url": "https://actualizado.com/imagen.jpg",
    }

    response = client.put(
        ANNOUNCEMENT_ID_URL.format(announcement_id=announcement.id), json=update_data,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Anuncio Actualizado"
    assert data["url"] == "https://actualizado.com"
    assert data["image_url"] == "https://actualizado.com/imagen.jpg"
    assert data["id"] == str(announcement.id)


def test_update_announcement_not_found(client: TestClient):
    """Test para verificar el comportamiento al actualizar un anuncio que no existe.
    """
    fake_announcement_id = uuid.uuid4()
    update_data = {"name": "Anuncio Actualizado"}

    response = client.put(
        ANNOUNCEMENT_ID_URL.format(announcement_id=fake_announcement_id),
        json=update_data,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anuncio no encontrado"


def test_delete_announcement_success(client: TestClient, db_session_test: Session):
    """Test para eliminar un anuncio exitosamente.
    """
    announcement = create_test_announcement(db_session_test)

    response = client.delete(
        ANNOUNCEMENT_ID_URL.format(announcement_id=announcement.id),
    )

    assert response.status_code == 204

    # Verificar que el anuncio ya no existe
    get_response = client.get(
        ANNOUNCEMENT_ID_URL.format(announcement_id=announcement.id),
    )
    assert get_response.status_code == 404


def test_delete_announcement_not_found(client: TestClient):
    """Test para verificar el comportamiento al eliminar un anuncio que no existe.
    """
    fake_announcement_id = uuid.uuid4()

    response = client.delete(
        ANNOUNCEMENT_ID_URL.format(announcement_id=fake_announcement_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anuncio no encontrado"


# Tests para relaciones muchos a muchos


def test_add_announcement_to_blog_post_success(
    client: TestClient, db_session_test: Session,
):
    """Test para agregar un anuncio a un blog post exitosamente.
    """
    blog_post = create_test_blog_post(db_session_test)
    announcement = create_test_announcement(db_session_test)

    response = client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=announcement.id,
        ),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(announcement.id)


def test_add_announcement_to_blog_post_blog_post_not_found(
    client: TestClient, db_session_test: Session,
):
    """Test para verificar el comportamiento cuando el blog post no existe.
    """
    fake_blog_post_id = uuid.uuid4()
    announcement = create_test_announcement(db_session_test)

    response = client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=fake_blog_post_id, announcement_id=announcement.id,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Blog post no encontrado"


def test_add_announcement_to_blog_post_announcement_not_found(
    client: TestClient, db_session_test: Session,
):
    """Test para verificar el comportamiento cuando el anuncio no existe.
    """
    blog_post = create_test_blog_post(db_session_test)
    fake_announcement_id = uuid.uuid4()

    response = client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=fake_announcement_id,
        ),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anuncio no encontrado"


def test_remove_announcement_from_blog_post_success(
    client: TestClient, db_session_test: Session,
):
    """Test para eliminar un anuncio de un blog post exitosamente.
    """
    blog_post = create_test_blog_post(db_session_test)
    announcement = create_test_announcement(db_session_test)

    # Primero agregar el anuncio al blog post
    client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=announcement.id,
        ),
    )

    # Luego eliminarlo
    response = client.delete(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=announcement.id,
        ),
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(announcement.id)


def test_get_blog_posts_for_announcement_success(
    client: TestClient, db_session_test: Session,
):
    """Test para obtener blog posts de un anuncio exitosamente.
    """
    announcement = create_test_announcement(db_session_test)
    blog_post1 = create_test_blog_post(db_session_test, title="Blog Post 1")
    blog_post2 = create_test_blog_post(db_session_test, title="Blog Post 2")

    # Agregar el anuncio a los blog posts
    client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post1.id, announcement_id=announcement.id,
        ),
    )
    client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post2.id, announcement_id=announcement.id,
        ),
    )

    response = client.get(
        ANNOUNCEMENT_BLOG_POSTS_URL.format(announcement_id=announcement.id),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    blog_post_titles = [bp["title"] for bp in data]
    assert "Blog Post 1" in blog_post_titles
    assert "Blog Post 2" in blog_post_titles


def test_get_blog_posts_for_announcement_not_found(client: TestClient):
    """Test para verificar el comportamiento cuando el anuncio no existe.
    """
    fake_announcement_id = uuid.uuid4()

    response = client.get(
        ANNOUNCEMENT_BLOG_POSTS_URL.format(announcement_id=fake_announcement_id),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Anuncio no encontrado"


def test_get_announcements_by_blog_post_success(
    client: TestClient, db_session_test: Session,
):
    """Test para obtener anuncios por blog post exitosamente.
    """
    blog_post = create_test_blog_post(db_session_test)
    announcement1 = create_test_announcement(db_session_test, name="Anuncio 1")
    announcement2 = create_test_announcement(db_session_test, name="Anuncio 2")

    # Agregar anuncios al blog post
    client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=announcement1.id,
        ),
    )
    client.post(
        ANNOUNCEMENT_TO_BLOG_POST_URL.format(
            blog_post_id=blog_post.id, announcement_id=announcement2.id,
        ),
    )

    response = client.get(
        ANNOUNCEMENTS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id),
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    announcement_names = [announcement["name"] for announcement in data]
    assert "Anuncio 1" in announcement_names
    assert "Anuncio 2" in announcement_names


def test_get_announcements_by_blog_post_not_found(client: TestClient):
    """Test para verificar el comportamiento cuando el blog post no existe.
    """
    fake_blog_post_id = uuid.uuid4()

    response = client.get(
        ANNOUNCEMENTS_BY_BLOG_POST_URL.format(blog_post_id=fake_blog_post_id),
    )

    assert response.status_code == 404
    assert "Blog post con id" in response.json()["detail"]


def test_get_announcements_by_blog_post_empty(
    client: TestClient, db_session_test: Session,
):
    """Test para obtener anuncios de un blog post que no tiene anuncios.
    """
    blog_post = create_test_blog_post(db_session_test)

    response = client.get(
        ANNOUNCEMENTS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id),
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_announcements_by_blog_post_with_pagination(
    client: TestClient, db_session_test: Session,
):
    """Test para verificar la paginación en la obtención de anuncios por blog post.
    """
    blog_post = create_test_blog_post(db_session_test)

    # Crear 5 anuncios y agregarlos al blog post
    announcements = []
    for i in range(1, 6):
        announcement = create_test_announcement(db_session_test, name=f"Anuncio {i}")
        announcements.append(announcement)
        client.post(
            ANNOUNCEMENT_TO_BLOG_POST_URL.format(
                blog_post_id=blog_post.id, announcement_id=announcement.id,
            ),
        )

    # Obtener los primeros 3 anuncios
    response = client.get(
        ANNOUNCEMENTS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id)
        + "?skip=0&limit=3",
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    # Obtener los siguientes 2 anuncios
    response = client.get(
        ANNOUNCEMENTS_BY_BLOG_POST_URL.format(blog_post_id=blog_post.id)
        + "?skip=3&limit=3",
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
