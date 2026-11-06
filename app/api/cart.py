"""Shopping cart API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.cart import CartResponse
from app.services import cart_service

router = APIRouter(prefix="/cart", tags=["Shopping cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's shopping cart."""
    cart = await cart_service.get_or_create_cart(db, current_user.id)
    return {
        "id": cart.id,
        "items": cart.items,
        "total_price": cart_service.calculate_total(cart),
    }


@router.post("/{movie_id}", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a movie to the shopping cart."""
    try:
        cart = await cart_service.add_item(db, current_user.id, movie_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "id": cart.id,
        "items": cart.items,
        "total_price": cart_service.calculate_total(cart),
    }


@router.delete("/{movie_id}", response_model=CartResponse)
async def remove_from_cart(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Remove a movie from the shopping cart."""
    try:
        cart = await cart_service.remove_item(db, current_user.id, movie_id)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "id": cart.id,
        "items": cart.items,
        "total_price": cart_service.calculate_total(cart),
    }


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Clear all items from the shopping cart."""
    await cart_service.clear_cart(db, current_user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
