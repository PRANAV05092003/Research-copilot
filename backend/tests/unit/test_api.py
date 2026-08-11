from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app
from app.models import User

client = TestClient(app)


def test_auth_login_invalid_credentials():
    mock_session = AsyncMock()

    # Mock result for user query
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.post(
        "/api/v1/auth/login", json={"email": "test@example.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

    app.dependency_overrides = {}


def test_auth_register_existing_email():
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id="123", email="test@example.com")
    mock_session.execute.return_value = mock_result

    app.dependency_overrides[get_db] = lambda: mock_session

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "strongpassword", "full_name": "Test User"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"

    app.dependency_overrides = {}


def test_validation_error():
    # Send a request with invalid schema (e.g. missing required field)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "password": "strongpassword"
            # missing email
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data

    # Check if the validation error structure contains expected info
    errors = data["errors"]
    assert "email" in str(errors)


def test_get_current_user_unauthorized():
    # Access a protected route without token
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
