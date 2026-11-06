"""Services for user favorite movies."""
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interaction import Favorite
from app.models.movie import Movie


async def add_favorite(db: AsyncSession, user_id: int, movie_id: int) -> Favorite:
    """Add a movie to the user's favorites."""
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise ValueError("Movie not found")

    existing = await db.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id, Favorite.movie_id == movie_id
        )
    )
    if existing:
        raise ValueError("Movie is already in favorites")

    favorite = Favorite(user_id=user_id, movie_id=movie_id)
    db.add(favorite)
    await db.commit()
    return await get_favorite(db, user_id, movie_id)


async def get_favorite(
    db: AsyncSession, user_id: int, movie_id: int
) -> Favorite | None:
    """Get a favorite entry with the movie details."""
    statement = (
        select(Favorite)
        .where(Favorite.user_id == user_id, Favorite.movie_id == movie_id)
        .options(
            selectinload(Favorite.movie).selectinload(Movie.certification),
            selectinload(Favorite.movie).selectinload(Movie.genres),
            selectinload(Favorite.movie).selectinload(Movie.directors),
            selectinload(Favorite.movie).selectinload(Movie.stars),
        )
    )
    return await db.scalar(statement)


async def list_favorites(
    db: AsyncSession, user_id: int, page: int, page_size: int
) -> tuple[Sequence[Favorite], int]:
    """List a user's favorite movies with pagination."""
    total = await db.scalar(
        select(func.count(Favorite.id)).where(Favorite.user_id == user_id)
    ) or 0
    statement = (
        select(Favorite)
        .where(Favorite.user_id == user_id)
        .options(
            selectinload(Favorite.movie).selectinload(Movie.certification),
            selectinload(Favorite.movie).selectinload(Movie.genres),
            selectinload(Favorite.movie).selectinload(Movie.directors),
            selectinload(Favorite.movie).selectinload(Movie.stars),
        )
        .order_by(Favorite.added_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(statement)
    return result.scalars().unique().all(), total


async def remove_favorite(db: AsyncSession, user_id: int, movie_id: int) -> bool:
    """Remove a movie from the user's favorites."""
    favorite = await db.scalar(
        select(Favorite).where(
            Favorite.user_id == user_id, Favorite.movie_id == movie_id
        )
    )
    if not favorite:
        return False
    await db.delete(favorite)
    await db.commit()
    return True
