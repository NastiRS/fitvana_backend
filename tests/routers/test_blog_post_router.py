import uuid

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.domain.models.blog_post import BlogPost
from src.domain.models.blog_post_tag_link import BlogPostTagLink
from tests.fixtures import (
    BLOG_POST_BASE_URL,
    BLOG_POST_ID_URL,
    CATEGORY_URL,
    GET_CATEGORY_URL,
    TAG_URL,
    TAGS_URL,
    create_test_blog_post,
    create_test_category,
    create_test_tag,
)


def test_create_blog_post_success(client: TestClient, db_session_test: Session):
    """Prueba la creación exitosa de un blog post."""
    test_category = create_test_category(db_session_test, name="Tech Blog Categoria")

    blog_post_data_payload = {
        "title": "Mi Primer Post de Prueba",
        "content": "Este es el contenido de mi post.",
        "category_id": str(test_category.id),
    }

    response = client.post(BLOG_POST_BASE_URL, json=blog_post_data_payload)
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["title"] == blog_post_data_payload["title"]
    assert data["content"] == blog_post_data_payload["content"]
    assert data["category_id"] == blog_post_data_payload["category_id"]
    assert "id" in data
    blog_post_id = data["id"]
    assert uuid.UUID(blog_post_id)
    assert data["category"] is not None
    assert data["category"]["id"] == str(test_category.id)
    assert data["tags"] == []

    stmt = select(BlogPost).where(BlogPost.id == uuid.UUID(blog_post_id))
    db_blog_post = db_session_test.exec(stmt).first()
    assert db_blog_post is not None
    assert db_blog_post.title == blog_post_data_payload["title"]
    assert db_blog_post.category_id == test_category.id


def test_read_blog_post_success(client: TestClient, db_session_test: Session):
    """Prueba la lectura exitosa de un blog post."""
    category = create_test_category(db_session_test, name="Lectura Categoria")
    post_title = "Post para Leer"
    post_content = "Contenido detallado."
    new_post = create_test_blog_post(
        db_session_test, title=post_title, content=post_content, category_id=category.id,
    )
    created_post_id = new_post.id

    response = client.get(BLOG_POST_ID_URL.format(blog_post_id=created_post_id))
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(created_post_id)
    assert data["title"] == post_title
    assert data["content"] == post_content
    assert data["category"]["id"] == str(category.id)
    assert data["tags"] == []


def test_read_blog_post_not_found(client: TestClient):
    """Prueba la lectura de un blog post que no existe."""
    non_existent_id = str(uuid.uuid4())
    response = client.get(BLOG_POST_ID_URL.format(blog_post_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "BlogPost no encontrado"


def test_read_blog_posts_empty(client: TestClient, db_session_test: Session):
    """Prueba la lectura de blog posts cuando no hay ninguno."""
    all_posts = db_session_test.exec(select(BlogPost)).all()
    for post in all_posts:
        db_session_test.delete(post)
    db_session_test.commit()

    response = client.get(BLOG_POST_BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_update_blog_post_success(client: TestClient, db_session_test: Session):
    """Prueba la actualización exitosa de un blog post."""
    category = create_test_category(db_session_test, name="Update Categoria")
    original_post = create_test_blog_post(
        db_session_test,
        title="Título Original Post",
        content="Contenido Original",
        category_id=category.id,
    )
    post_id_to_update = original_post.id

    update_payload = {
        "title": "Título Actualizado Post",
        "content": "Contenido Actualizado.",
    }
    response = client.put(
        BLOG_POST_ID_URL.format(blog_post_id=post_id_to_update), json=update_payload,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(post_id_to_update)
    assert data["title"] == update_payload["title"]
    assert data["content"] == update_payload["content"]

    db_session_test.refresh(original_post)
    assert original_post.title == update_payload["title"]
    assert original_post.content == update_payload["content"]


def test_delete_blog_post_success(client: TestClient, db_session_test: Session):
    """Prueba la eliminación exitosa de un blog post."""
    category = create_test_category(db_session_test, name="Delete Categoria")
    post_to_delete = create_test_blog_post(
        db_session_test, title="Post a Eliminar", content="Bye", category_id=category.id,
    )
    post_id = post_to_delete.id

    delete_response = client.delete(BLOG_POST_ID_URL.format(blog_post_id=post_id))
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    stmt = select(BlogPost).where(BlogPost.id == post_id)
    db_post = db_session_test.exec(stmt).first()
    assert db_post is None

    get_response = client.get(BLOG_POST_ID_URL.format(blog_post_id=post_id))
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_add_tag_to_blog_post_success(client: TestClient, db_session_test: Session):
    """Prueba agregar un tag a un blog post exitosamente."""
    blog_post = create_test_blog_post(db_session_test)
    tag = create_test_tag(db_session_test, name="Tag Prueba 1")

    response = client.post(TAG_URL.format(blog_post_id=blog_post.id, tag_id=tag.id))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(blog_post.id)
    assert len(data["tags"]) == 1
    assert data["tags"][0]["id"] == str(tag.id)
    assert data["tags"][0]["name"] == tag.name

    stmt = select(BlogPostTagLink).where(
        BlogPostTagLink.blog_post_id == blog_post.id, BlogPostTagLink.tag_id == tag.id,
    )
    link = db_session_test.exec(stmt).first()
    assert link is not None


def test_add_tag_to_blog_post_not_found(client: TestClient, db_session_test: Session):
    """Prueba agregar un tag a un blog post que no existe."""
    tag = create_test_tag(db_session_test, name="Tag Prueba No Post")
    non_existent_id = str(uuid.uuid4())

    response = client.post(TAG_URL.format(blog_post_id=non_existent_id, tag_id=tag.id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in response.json()["detail"]


def test_add_tag_to_blog_post_tag_not_found(
    client: TestClient, db_session_test: Session,
):
    """Prueba agregar un tag que no existe a un blog post."""
    blog_post = create_test_blog_post(db_session_test)
    non_existent_tag_id = str(uuid.uuid4())

    response = client.post(
        TAG_URL.format(blog_post_id=blog_post.id, tag_id=non_existent_tag_id),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in response.json()["detail"]


def test_remove_tag_from_blog_post_success(
    client: TestClient, db_session_test: Session,
):
    """Prueba eliminar un tag de un blog post exitosamente."""
    blog_post = create_test_blog_post(db_session_test)
    tag = create_test_tag(db_session_test, name="Tag Para Eliminar")

    blog_post.tags.append(tag)
    db_session_test.add(blog_post)
    db_session_test.commit()
    db_session_test.refresh(blog_post)

    assert len(blog_post.tags) == 1

    response = client.delete(TAG_URL.format(blog_post_id=blog_post.id, tag_id=tag.id))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(blog_post.id)
    assert len(data["tags"]) == 0

    db_session_test.refresh(blog_post)
    assert len(blog_post.tags) == 0

    stmt = select(BlogPostTagLink).where(
        BlogPostTagLink.blog_post_id == blog_post.id, BlogPostTagLink.tag_id == tag.id,
    )
    link = db_session_test.exec(stmt).first()
    assert link is None


def test_get_blog_post_tags_success(client: TestClient, db_session_test: Session):
    """Prueba obtener todos los tags de un blog post."""
    blog_post = create_test_blog_post(db_session_test)
    tag1 = create_test_tag(db_session_test, name="Tag1")
    tag2 = create_test_tag(db_session_test, name="Tag2")

    blog_post.tags.append(tag1)
    blog_post.tags.append(tag2)
    db_session_test.add(blog_post)
    db_session_test.commit()
    db_session_test.refresh(blog_post)

    response = client.get(TAGS_URL.format(blog_post_id=blog_post.id))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert len(data) == 2
    tag_names = [tag["name"] for tag in data]
    assert "Tag1" in tag_names
    assert "Tag2" in tag_names


def test_get_blog_post_tags_empty(client: TestClient, db_session_test: Session):
    """Prueba obtener tags de un blog post que no tiene ninguno."""
    blog_post = create_test_blog_post(db_session_test)

    response = client.get(TAGS_URL.format(blog_post_id=blog_post.id))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_assign_category_to_blog_post_success(
    client: TestClient, db_session_test: Session,
):
    """Prueba asignar una categoría a un blog post exitosamente."""
    initial_category = create_test_category(db_session_test, name="Categoría Inicial")
    blog_post = create_test_blog_post(db_session_test, category_id=initial_category.id)

    new_category = create_test_category(db_session_test, name="Nueva Categoría")

    response = client.put(
        CATEGORY_URL.format(blog_post_id=blog_post.id, category_id=new_category.id),
    )
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(blog_post.id)
    assert data["category_id"] == str(new_category.id)
    assert data["category"]["id"] == str(new_category.id)
    assert data["category"]["name"] == new_category.name

    # Verificar en la base de datos
    db_session_test.refresh(blog_post)
    assert blog_post.category_id == new_category.id


def test_assign_category_to_blog_post_not_found(
    client: TestClient, db_session_test: Session,
):
    """Prueba asignar una categoría a un blog post que no existe."""
    category = create_test_category(db_session_test, name="Categoría Sin Post")
    non_existent_id = str(uuid.uuid4())

    response = client.put(
        CATEGORY_URL.format(blog_post_id=non_existent_id, category_id=category.id),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in response.json()["detail"]


def test_assign_category_to_blog_post_category_not_found(
    client: TestClient, db_session_test: Session,
):
    """Prueba asignar una categoría que no existe a un blog post."""
    blog_post = create_test_blog_post(db_session_test)
    non_existent_category_id = str(uuid.uuid4())

    response = client.put(
        CATEGORY_URL.format(
            blog_post_id=blog_post.id, category_id=non_existent_category_id,
        ),
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrada" in response.json()["detail"]


def test_get_blog_post_category_success(client: TestClient, db_session_test: Session):
    """Prueba obtener la categoría de un blog post."""
    category = create_test_category(db_session_test, name="Categoría a Obtener")
    blog_post = create_test_blog_post(db_session_test, category_id=category.id)

    response = client.get(GET_CATEGORY_URL.format(blog_post_id=blog_post.id))
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == str(category.id)
    assert data["name"] == category.name


def test_get_blog_post_category_blog_post_not_found(
    client: TestClient, db_session_test: Session,
):
    """Prueba obtener la categoría de un blog post que no existe."""
    non_existent_id = str(uuid.uuid4())

    response = client.get(GET_CATEGORY_URL.format(blog_post_id=non_existent_id))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in response.json()["detail"]
