import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.main import app


class StubSession:
    """execute() 호출만 흉내내는 최소한의 세션 대역."""

    def __init__(self, error: Exception | None = None) -> None:
        self._error = error

    def execute(self, statement):
        if self._error is not None:
            raise self._error
        return None


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def use_session(session: StubSession) -> None:
    app.dependency_overrides[get_db] = lambda: session


def test_read_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "Secret Backend Project"}


def test_health_db_returns_ok(client):
    use_session(StubSession())

    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"database": "ok"}


def test_health_db_returns_503_when_database_is_down(client):
    use_session(StubSession(SQLAlchemyError("connection refused")))

    response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
