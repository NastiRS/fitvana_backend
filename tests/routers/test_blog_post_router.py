import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import date

from app.domain.models.blog_post import BlogPost
from app.domain.models.category import Category
from app.domain.models.tag import Tag

BLOG_POST_BASE_URL = "/v1/api/blog_posts"
BLOG_POST_ID_URL = "/v1/api/blog_posts/{blog_post_id}"


def create_test_category(
    db_session: Session,
    name: str = "Categoría de Prueba para Blog",
    description: str = "Desc",
) -> Category:
    category = Category(name=name, description=description)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def create_test_tag(db_session: Session, name: str = "Tag de Prueba para Blog") -> Tag:
    tag = Tag(name=name)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


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
    new_post = BlogPost(
        title=post_title,
        content=post_content,
        category_id=category.id,
        date=date.today(),
    )
    db_session_test.add(new_post)
    db_session_test.commit()
    db_session_test.refresh(new_post)
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
    original_post = BlogPost(
        title="Título Original Post",
        content="Contenido Original",
        category_id=category.id,
        date=date.today(),
    )
    db_session_test.add(original_post)
    db_session_test.commit()
    db_session_test.refresh(original_post)
    post_id_to_update = original_post.id

    update_payload = {
        "title": "Título Actualizado Post",
        "content": "Contenido Actualizado.",
    }
    response = client.put(
        BLOG_POST_ID_URL.format(blog_post_id=post_id_to_update), json=update_payload
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
    post_to_delete = BlogPost(
        title="Post a Eliminar",
        content="Bye",
        category_id=category.id,
        date=date.today(),
    )
    db_session_test.add(post_to_delete)
    db_session_test.commit()
    db_session_test.refresh(post_to_delete)
    post_id = post_to_delete.id

    delete_response = client.delete(BLOG_POST_ID_URL.format(blog_post_id=post_id))
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    stmt = select(BlogPost).where(BlogPost.id == post_id)
    db_post = db_session_test.exec(stmt).first()
    assert db_post is None

    get_response = client.get(BLOG_POST_ID_URL.format(blog_post_id=post_id))
    assert get_response.status_code == status.HTTP_404_NOT_FOUND
