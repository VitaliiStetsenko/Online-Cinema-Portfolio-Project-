"""Integration tests for ratings, comments, and shopping cart."""

from httpx import AsyncClient

from app.models.movie import Movie


async def test_rating_and_comment_lifecycle(
    client: AsyncClient,
    auth_headers: dict[str, str],
    other_auth_headers: dict[str, str],
    movie: Movie,
) -> None:
    """Users rate films and manage only their own comments."""
    rating = await client.put(f"/api/movies/{movie.id}/rating", headers=auth_headers, json={"score": 8})
    assert rating.status_code == 200
    assert rating.json()["score"] == 8

    rating_update = await client.put(f"/api/movies/{movie.id}/rating", headers=auth_headers, json={"score": 9})
    assert rating_update.status_code == 200

    summary = await client.get(f"/api/movies/{movie.id}/rating", headers=auth_headers)
    assert summary.json() == {"movie_id": movie.id, "average_score": 9.0, "ratings_count": 1, "user_score": 9}

    created = await client.post(
        f"/api/movies/{movie.id}/comments", headers=auth_headers, json={"text": "Excellent movie"}
    )
    assert created.status_code == 201
    comment_id = created.json()["id"]

    forbidden = await client.put(f"/api/comments/{comment_id}", headers=other_auth_headers, json={"text": "Changed"})
    assert forbidden.status_code == 403

    reaction = await client.put(f"/api/comments/{comment_id}/reaction?is_like=true", headers=other_auth_headers)
    assert reaction.status_code == 200
    assert reaction.json()["likes_count"] == 1

    updated = await client.put(f"/api/comments/{comment_id}", headers=auth_headers, json={"text": "Still excellent"})
    assert updated.status_code == 200
    assert updated.json()["text"] == "Still excellent"

    deleted = await client.delete(f"/api/comments/{comment_id}", headers=auth_headers)
    assert deleted.status_code == 204


async def test_cart_lifecycle_and_duplicate_protection(
    client: AsyncClient, auth_headers: dict[str, str], movie: Movie
) -> None:
    """Users can manage cart items and cannot add duplicates."""
    empty_cart = await client.get("/api/cart", headers=auth_headers)
    assert empty_cart.status_code == 200
    assert empty_cart.json()["items"] == []

    added = await client.post(f"/api/cart/{movie.id}", headers=auth_headers)
    assert added.status_code == 201
    assert added.json()["total_price"] == "9.99"

    duplicate = await client.post(f"/api/cart/{movie.id}", headers=auth_headers)
    assert duplicate.status_code == 400

    removed = await client.delete(f"/api/cart/{movie.id}", headers=auth_headers)
    assert removed.status_code == 200
    assert removed.json()["items"] == []

    missing = await client.delete(f"/api/cart/{movie.id}", headers=auth_headers)
    assert missing.status_code == 400

    await client.post(f"/api/cart/{movie.id}", headers=auth_headers)
    cleared = await client.delete("/api/cart", headers=auth_headers)
    assert cleared.status_code == 204
    assert (await client.get("/api/cart", headers=auth_headers)).json()["items"] == []
