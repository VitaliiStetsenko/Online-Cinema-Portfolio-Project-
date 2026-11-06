"""Tests for security utilities."""

from app.core.security import get_password_hash, verify_password, create_access_token, decode_token


def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePassword123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)


def test_jwt_token_creation_and_decoding():
    """Test JWT token creation and decoding."""
    data = {"sub": "123"}
    token = create_access_token(data)

    assert token is not None
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"


def test_invalid_token_decoding():
    """Test decoding invalid token."""
    invalid_token = "invalid.token.here"
    decoded = decode_token(invalid_token)
    assert decoded is None
