import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from fastapi.testclient import TestClient

from app.core.security import create_access_token, get_password_hash, hash_refresh_token
from app.db.session import get_db
from app.main import app
from app.models import RefreshToken, User, Workspace

client = TestClient(app)

def test_login_valid_credentials():
    mock_session = AsyncMock()
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("ValidPass123!"),
        is_active=True,
        created_at=datetime.now(UTC)
    )
    workspace = Workspace(id=uuid.uuid4(), owner_id=user.id)
    
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = user
    
    mock_ws_result = MagicMock()
    mock_ws_result.scalars().first.return_value = workspace
    
    mock_session.execute.side_effect = [mock_user_result, mock_ws_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = client.post("/api/v1/auth/login", json={"email": "test@example.com", "password": "ValidPass123!"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "refresh_token" in response.cookies
    
    app.dependency_overrides = {}

def test_refresh_valid_token():
    mock_session = AsyncMock()
    
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        is_active=True
    )
    
    workspace = Workspace(id=uuid.uuid4(), owner_id=user.id)
    
    db_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=user.id,
        token_hash=hash_refresh_token("valid_refresh_token"),
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked_at=None
    )
    
    mock_token_result = MagicMock()
    mock_token_result.scalar_one_or_none.return_value = db_token
    
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = user
    
    mock_ws_result = MagicMock()
    mock_ws_result.scalars().first.return_value = workspace
    
    mock_session.execute.side_effect = [mock_token_result, mock_user_result, mock_ws_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    client.cookies.set("refresh_token", "valid_refresh_token")
    response = client.post("/api/v1/auth/refresh")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    # verify db_token got revoked
    assert db_token.revoked_at is not None
    
    app.dependency_overrides = {}
    client.cookies.clear()

def test_refresh_revoked_token():
    mock_session = AsyncMock()
    
    db_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_hash=hash_refresh_token("revoked_token"),
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked_at=datetime.now(UTC) - timedelta(days=1)
    )
    
    mock_token_result = MagicMock()
    mock_token_result.scalar_one_or_none.return_value = db_token
    
    # After revocation is detected, it executes an update query
    mock_update_result = MagicMock()
    
    mock_session.execute.side_effect = [mock_token_result, mock_update_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    client.cookies.set("refresh_token", "revoked_token")
    response = client.post("/api/v1/auth/refresh")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token revoked"
    
    app.dependency_overrides = {}
    client.cookies.clear()

def test_refresh_expired_token():
    mock_session = AsyncMock()
    
    db_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_hash=hash_refresh_token("expired_token"),
        expires_at=datetime.now(UTC) - timedelta(days=1),
        revoked_at=None
    )
    
    mock_token_result = MagicMock()
    mock_token_result.scalar_one_or_none.return_value = db_token
    
    mock_session.execute.side_effect = [mock_token_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    client.cookies.set("refresh_token", "expired_token")
    response = client.post("/api/v1/auth/refresh")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token expired"
    
    app.dependency_overrides = {}
    client.cookies.clear()

def test_logout():
    mock_session = AsyncMock()
    
    db_token = RefreshToken(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        token_hash=hash_refresh_token("valid_token"),
        expires_at=datetime.now(UTC) + timedelta(days=7),
        revoked_at=None
    )
    
    mock_token_result = MagicMock()
    mock_token_result.scalar_one_or_none.return_value = db_token
    
    mock_session.execute.side_effect = [mock_token_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    client.cookies.set("refresh_token", "valid_token")
    response = client.post("/api/v1/auth/logout")
    
    assert response.status_code == 200
    assert db_token.revoked_at is not None
    assert response.cookies.get("refresh_token") is None or response.cookies.get("refresh_token") == ""
    
    app.dependency_overrides = {}
    client.cookies.clear()

def test_get_me_valid():
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        is_active=True,
        created_at=datetime.now(UTC)
    )
    
    token = create_access_token(subject=user.id)
    
    mock_session = AsyncMock()
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = user
    mock_session.execute.side_effect = [mock_user_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"
    
    app.dependency_overrides = {}

def test_get_me_inactive():
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        is_active=False,
        created_at=datetime.now(UTC)
    )
    
    token = create_access_token(subject=user.id)
    
    mock_session = AsyncMock()
    mock_user_result = MagicMock()
    mock_user_result.scalar_one_or_none.return_value = user
    mock_session.execute.side_effect = [mock_user_result]
    
    app.dependency_overrides[get_db] = lambda: mock_session
    
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 401
    
    app.dependency_overrides = {}

def test_missing_bearer_token():
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"
