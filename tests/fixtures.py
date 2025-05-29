import uuid
from datetime import date
from sqlmodel import Session

from app.domain.models.category import Category
from app.domain.models.blog_post import BlogPost
from app.domain.models.tag import Tag
from app.domain.models.section import Section
from app.domain.models.announcement import Announcement


# URLs para tests de categorías
CATEGORY_BASE_URL = "/v1/api/categories"
CATEGORY_ID_URL = "/v1/api/categories/{category_id}"
BLOG_POSTS_BY_CATEGORY_URL = "/v1/api/categories/{category_id}/blog_posts"

# URLs para tests de blog posts
BLOG_POST_BASE_URL = "/v1/api/blog_posts"
BLOG_POST_ID_URL = "/v1/api/blog_posts/{blog_post_id}"
TAG_URL = "/v1/api/blog_posts/{blog_post_id}/tags/{tag_id}"
TAGS_URL = "/v1/api/blog_posts/{blog_post_id}/tags"
CATEGORY_URL = "/v1/api/blog_posts/{blog_post_id}/category/{category_id}"
GET_CATEGORY_URL = "/v1/api/blog_posts/{blog_post_id}/category"

# URLs para tests de tags
TAG_BASE_URL = "/v1/api/tags"
TAG_ID_URL = "/v1/api/tags/{tag_id}"

# URLs para tests de sections
SECTION_BASE_URL = "/v1/api/sections"
SECTION_ID_URL = "/v1/api/sections/{section_id}"
SECTIONS_BY_BLOG_POST_URL = "/v1/api/sections/blog_post/{blog_post_id}"

# URLs para tests de announcements
ANNOUNCEMENT_BASE_URL = "/v1/api/announcements"
ANNOUNCEMENT_ID_URL = "/v1/api/announcements/{announcement_id}"
ANNOUNCEMENT_TO_BLOG_POST_URL = (
    "/v1/api/announcements/blog_post/{blog_post_id}/announcements/{announcement_id}"
)
ANNOUNCEMENT_BLOG_POSTS_URL = "/v1/api/announcements/{announcement_id}/blog_posts"
ANNOUNCEMENTS_BY_BLOG_POST_URL = "/v1/api/announcements/blog_post/{blog_post_id}"


def create_test_category(
    db_session: Session,
    name: str = "Categoría de Prueba",
    description: str = "Descripción de prueba",
) -> Category:
    """
    Crea una categoría de prueba en la base de datos.
    """
    category = Category(name=name, description=description)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


def create_test_tag(db_session: Session, name: str = "Tag de Prueba") -> Tag:
    """
    Crea un tag de prueba en la base de datos.
    """
    tag = Tag(name=name)
    db_session.add(tag)
    db_session.commit()
    db_session.refresh(tag)
    return tag


def create_test_blog_post(
    db_session: Session,
    title: str = "Blog Post de Prueba",
    content: str = "Contenido de prueba",
    category_id: uuid.UUID = None,
) -> BlogPost:
    """
    Crea un blog post de prueba en la base de datos.
    Si no se proporciona category_id, crea automáticamente una categoría.
    """
    category_id = category_id or create_test_category(db_session).id

    blog_post = BlogPost(
        title=title,
        content=content,
        category_id=category_id,
        date=date.today(),
    )
    db_session.add(blog_post)
    db_session.commit()
    db_session.refresh(blog_post)
    return blog_post


def create_test_section(
    db_session: Session,
    title: str = "Sección de Prueba",
    content: str = "Contenido de la sección de prueba",
    position_order: int = 1,
    image_url: str = None,
    blog_post_id: uuid.UUID = None,
) -> Section:
    """
    Crea una sección de prueba en la base de datos.
    Si no se proporciona blog_post_id, crea automáticamente un blog post.
    """
    blog_post_id = blog_post_id or create_test_blog_post(db_session).id

    section = Section(
        title=title,
        content=content,
        position_order=position_order,
        image_url=image_url,
        blog_post_id=blog_post_id,
    )
    db_session.add(section)
    db_session.commit()
    db_session.refresh(section)
    return section


def create_test_announcement(
    db_session: Session,
    name: str = "Anuncio de Prueba",
    url: str = "https://example.com",
    image_url: str = "https://example.com/image.jpg",
) -> Announcement:
    """
    Crea un anuncio de prueba en la base de datos.
    """
    announcement = Announcement(
        name=name,
        url=url,
        image_url=image_url,
    )
    db_session.add(announcement)
    db_session.commit()
    db_session.refresh(announcement)
    return announcement
