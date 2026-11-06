"""Integration tests for profiles and favorite movies."""

from httpx import AsyncClient

from app.models.movie import Movie


async def test_create_update_and_view_profile(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Users can manage their own profile."""
    created = await client.post(
        "/api/users/me/profile",
        headers=auth_headers,
        json={"first_name": "Vitalii", "last_name": "Test", "info": "Cinema fan"},
    )
    assert created.status_code == 201
    assert created.json()["first_name"] == "Vitalii"

    duplicate = await client.post("/api/users/me/profile", headers=auth_headers, json={})
    assert duplicate.status_code == 400

    updated = await client.put("/api/users/me/profile", headers=auth_headers, json={"info": "Updated"})
    assert updated.status_code == 200
    assert updated.json()["info"] == "Updated"

    current = await client.get("/api/users/me", headers=auth_headers)
    assert current.status_code == 200
    assert current.json()["profile"]["info"] == "Updated"


async def test_favorite_lifecycle(client: AsyncClient, auth_headers: dict[str, str], movie: Movie) -> None:
    """Users can add, list, and remove favorite movies."""
    added = await client.post(f"/api/favorites/{movie.id}", headers=auth_headers)
    assert added.status_code == 201
    assert added.json()["movie"]["id"] == movie.id

    duplicate = await client.post(f"/api/favorites/{movie.id}", headers=auth_headers)
    assert duplicate.status_code == 400

    favorites = await client.get("/api/favorites", headers=auth_headers)
    assert favorites.status_code == 200
    assert favorites.json()["total"] == 1

    removed = await client.delete(f"/api/favorites/{movie.id}", headers=auth_headers)
    assert removed.status_code == 204
    assert (await client.delete(f"/api/favorites/{movie.id}", headers=auth_headers)).status_code == 404
