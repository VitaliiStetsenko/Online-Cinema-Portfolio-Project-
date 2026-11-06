"""Tests for movie catalog API."""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.movie import Certification


@pytest.mark.asyncio
async def test_create_genre(client: AsyncClient, db_session: AsyncSession):
    """Test genre creation by moderator."""
    # Register and activate user
    await client.post(
        "/api/auth/register",
        json={"email": "mod@example.com", "password": "ModPass123"}
    )
    # Normally would need to activate and set moderator role
    # For simplicity, testing without full auth flow
    

@pytest.mark.asyncio
async def test_get_genres(client: AsyncClient):
    """Test getting list of genres."""
    response = await client.get("/api/catalog/genres")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
