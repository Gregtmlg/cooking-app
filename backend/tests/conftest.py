import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.models.group import Group

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)


@pytest.fixture(scope="function")
def client(db_session, monkeypatch):
    monkeypatch.setattr(settings, "session_cookie_secure", False)
    def override_get_db():
        yield db_session


    fastapi_app.dependency_overrides[get_db] = override_get_db

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db_session():
    connection = engine_test.connect()
    Base.metadata.create_all(bind=connection)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=connection)
        connection.close()


@pytest.fixture
def amis_group(db_session):

    group = Group(slug="amis", name="Amis")
    db_session.add(group)
    db_session.commit()
    return group


@pytest.fixture
def account(db_session, amis_group):
    from app.services.account_service import create_account

    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="amis"
    )
    return account
