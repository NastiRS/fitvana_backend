from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from src.core.database.config import get_session as original_get_session
from src.domain.models.announcement import Announcement  # noqa: F401
from src.domain.models.base import Base
from src.domain.models.blog_post import BlogPost  # noqa: F401
from src.domain.models.blog_post_announcement_link import (
    BlogPostAnnouncementLink,  # noqa: F401
)
from src.domain.models.blog_post_tag_link import BlogPostTagLink  # noqa: F401
from src.domain.models.category import Category  # noqa: F401
from src.domain.models.section import Section  # noqa: F401
from src.domain.models.tag import Tag  # noqa: F401
from src.main import app
from tests.settings import test_db_settings

TEST_DATABASE_URL = (
    f"postgresql+psycopg2://{test_db_settings.TEST_DB_USERNAME}:{test_db_settings.TEST_DB_PASSWORD}@"
    f"{test_db_settings.TEST_DB_HOST}:{test_db_settings.TEST_DB_PORT}/{test_db_settings.TEST_DB_NAME}"
)

engine_test = create_engine(TEST_DATABASE_URL, echo=False)


@pytest.fixture(scope="session", autouse=True)
def create_test_database_tables():
    """Crea todas las tablas de la base de datos de prueba antes de que comience la sesión de pruebas
    y las elimina después de que todas las pruebas de la sesión hayan finalizado.
    """
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def db_session_test() -> Generator[Session]:
    """Proporciona una sesión de base de datos de prueba para cada función de prueba.
    Las transacciones se revierten después de cada prueba para asegurar el aislamiento.
    """
    connection = engine_test.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session_test: Session) -> Generator[TestClient]:
    """Proporciona una instancia de TestClient configurada con la base de datos de prueba.
    Anula la dependencia get_session de la aplicación para usar la sesión de prueba.
    """

    def get_session_override() -> Generator[Session]:
        yield db_session_test

    app.dependency_overrides[original_get_session] = get_session_override

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
