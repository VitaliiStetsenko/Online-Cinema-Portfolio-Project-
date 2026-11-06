"""Favorite movies API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.favorite import FavoriteListResponse, FavoriteResponse
from app.services import favorite_service

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/{movie_id}", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a movie to the current user's favorites."""
    try:
        return await favorite_service.add_favorite(db, current_user.id, movie_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("", response_model=FavoriteListResponse)
async def list_favorites(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List the current user's favorite movies."""
    items, total = await favorite_service.list_favorites(db, current_user.id, page, page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_favorite(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a movie from the current user's favorites."""
    deleted = await favorite_service.remove_favorite(db, current_user.id, movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Favorite movie not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
