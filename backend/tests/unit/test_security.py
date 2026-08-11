from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    get_password_hash,
    hash_refresh_token,
    verify_password,
)


def test_password_hashing():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert "argon2" in hashed
    
    # Valid password verification
    assert verify_password(password, hashed) is True
    
    # Invalid password
    assert verify_password("WrongPassword123!", hashed) is False
    
    # Empty password
    assert verify_password("", hashed) is False
    
    # Empty hashed password
    assert verify_password(password, "") is False
    assert verify_password(password, None) is False

def test_unicode_and_long_password():
    password = "🔐ñçü€" * 50
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password(password + "a", hashed) is False

def test_refresh_token():
    token1 = create_refresh_token()
    token2 = create_refresh_token()
    assert token1 != token2
    assert len(token1) == 64
    
    hashed1 = hash_refresh_token(token1)
    hashed2 = hash_refresh_token(token1)
    
    assert hashed1 == hashed2
    assert hashed1 != token1

def test_access_token_valid():
    subject = "user123"
    token = create_access_token(subject=subject, workspace_id="ws123")
    
    payload = decode_access_token(token)
    assert payload["sub"] == subject
    assert payload["type"] == "access"
    assert payload["wid"] == "ws123"
    assert "exp" in payload

def test_access_token_expired():
    # temporarily mock settings to force expiration
    original_ttl = settings.ACCESS_TOKEN_TTL_MINUTES
    settings.ACCESS_TOKEN_TTL_MINUTES = -1
    
    token = create_access_token(subject="user123")
    
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)
        
    settings.ACCESS_TOKEN_TTL_MINUTES = original_ttl

def test_access_token_invalid_signature():
    token = create_access_token(subject="user123")
    
    original_secret = settings.JWT_SECRET_KEY
    settings.JWT_SECRET_KEY = "wrong-secret"
    
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)
        
    settings.JWT_SECRET_KEY = original_secret

def test_access_token_invalid_type():
    expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode = {"exp": expire, "sub": "user123", "type": "refresh"}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    with pytest.raises(ValueError, match="Invalid token type"):
        decode_access_token(token)

def test_access_token_missing_claims():
    expire = datetime.now(UTC) + timedelta(minutes=15)
    
    # Missing type
    to_encode = {"exp": expire, "sub": "user123"}
    token = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)

def test_malformed_jwt():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("not.a.valid.jwt")
