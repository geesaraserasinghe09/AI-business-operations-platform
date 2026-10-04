import pytest
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token


def test_password_hashing():
    raw = "SecureBusinessOps2026!"
    hashed = get_password_hash(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_flow():
    user_id = "test-user-12345"
    role = "manager"
    token = create_access_token(subject=user_id, role=role)
    assert token is not None

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == user_id
    assert decoded["role"] == role
