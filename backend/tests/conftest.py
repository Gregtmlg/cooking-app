import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401
from app.core import rate_limit
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app
from app.models.group import Group
from app.models.recipe import Recipe

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
def chuteam_group(db_session):

    group = Group(slug="chuteam", name="ChuTeam")
    db_session.add(group)
    db_session.commit()
    return group


@pytest.fixture
def account(db_session, chuteam_group):
    from app.services.account_service import create_account

    account = create_account(
        db_session, username="Louise", password="motdepasse123", group_slug="chuteam"
    )
    return account


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    rate_limit._attempts.clear()
    yield
    rate_limit._attempts.clear()


@pytest.fixture
def auth_session(db_session, account):
    from app.models.session import AuthSession
    from app.services.session_service import _hash_token, create_session

    token = create_session(db_session, account.id)
    return db_session.get(AuthSession, _hash_token(token))


@pytest.fixture
def another_account(db_session, chuteam_group):
    from app.services.account_service import create_account

    return create_account(
        db_session, username="Autre", password="motdepasse123", group_slug="chuteam"
    )


@pytest.fixture
def multi_profile_account(db_session, chuteam_group):
    from app.models.profile import Profile
    from app.services.account_service import create_account

    account = create_account(
        db_session,
        username="Famille",
        password="motdepasse123",
        group_slug="chuteam",
        display_name="Michel",
    )

    # Second profil ajouté directement
    jeanne = Profile(display_name="Jeanne", account_id=account.id)
    jeanne.groups.append(chuteam_group)
    db_session.add(jeanne)
    db_session.commit()
    db_session.refresh(account)
    return account


@pytest.fixture
def auth_client(client, db_session, account):
    # create_account pose must_change_password = True : sans ça,
    # toute route recettes renverrait 403 PASSWORD_CHANGE_REQUIRED.
    account.must_change_password = False
    db_session.commit()
    response = client.post(
        "/api/v1/auth/login", json={"username": "Louise", "password": "motdepasse123"}
    )
    assert response.status_code == 200  # échec bruyant si le login casse
    return client


@pytest.fixture
def world(db_session):
    """Deux groupes, six profils, quatre recettes — un petit monde complet."""
    from app.services.account_service import create_account

    famille = Group(slug="famille", name="Famille")
    chuteam = Group(slug="chuteam", name="ChuTeam")
    db_session.add_all([famille, chuteam])
    db_session.commit()

    def profile(username, *slugs, admin=False):
        account = create_account(
            db_session, username=username, password="motdepasse123", is_admin=admin
        )
        p = account.profiles[0]
        p.groups.extend(g for g in (famille, chuteam) if g.slug in slugs)
        db_session.commit()
        return p

    profiles = {
        "auteur": profile("auteur"),  # sans groupe : propriétaire des recettes
        "lambda": profile("lambda"),  # sans groupe
        "fam": profile("fam", "famille"),
        "chu": profile("chu", "chuteam"),
        "multi": profile("multi", "famille", "chuteam"),
        "admin": profile("admin", admin=True),
    }

    def recipe(title, *, visible_to_all=False, audience=()):
        r = Recipe(
            title=title,
            instructions="…",
            owner_id=profiles["auteur"].id,
            visible_to_all=visible_to_all,
            audience=list(audience),
        )
        db_session.add(r)
        return r

    recipe("tous", visible_to_all=True)
    recipe("famille", audience=[famille])
    recipe("chuteam", audience=[chuteam])
    recipe("privee")
    db_session.commit()
    return profiles
