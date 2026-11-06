"""Tests for authentication API."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    response = await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "AnotherPass123"}
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_inactive_user(client: AsyncClient):
    """Test login with inactive account."""
    await client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    response = await client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "SecurePass123"}
    )
    assert response.status_code == 401
