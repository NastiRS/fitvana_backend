from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from src.core.database.settings import db_settings
from src.domain.models.announcement import Announcement  # noqa: F401
from src.domain.models.blog_post import BlogPost  # noqa: F401
from src.domain.models.blog_post_announcement_link import (
    BlogPostAnnouncementLink,  # noqa: F401
)
from src.domain.models.blog_post_tag_link import BlogPostTagLink  # noqa: F401
from src.domain.models.category import Category  # noqa: F401
from src.domain.models.section import Section  # noqa: F401
from src.domain.models.tag import Tag  # noqa: F401

username = db_settings.DB_USERNAME
password = db_settings.DB_PASSWORD
dbname = db_settings.DB_NAME
db_port = db_settings.DB_PORT
db_host = db_settings.DB_HOST

DATABASE_URL = (
    f"postgresql+psycopg2://{username}:{password}@{db_host}:{db_port}/{dbname}"
)
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session]:
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
