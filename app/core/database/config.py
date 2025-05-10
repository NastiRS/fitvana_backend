from sqlmodel import SQLModel, Session, create_engine

from app.domain.models.announcement import Announcement  # noqa: F401
from app.domain.models.category import Category  # noqa: F401
from app.domain.models.blog_post_announcement_link import BlogPostAnnouncementLink  # noqa: F401
from app.domain.models.blog_post_tag_link import BlogPostTagLink  # noqa: F401
from app.domain.models.blog_post import BlogPost  # noqa: F401
from app.domain.models.section import Section  # noqa: F401
from app.domain.models.tag import Tag  # noqa: F401


from typing import Generator

from app.core.database.settings import db_settings

username = db_settings.DB_USERNAME
password = db_settings.DB_PASSWORD
dbname = db_settings.DB_NAME
db_port = db_settings.DB_PORT
db_host = db_settings.DB_HOST

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{username}:{password}@{db_host}:{db_port}/{dbname}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
