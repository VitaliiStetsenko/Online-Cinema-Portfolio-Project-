"""Pydantic schemas for shopping cart."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.schemas.movie import MovieResponse


class CartItemResponse(BaseModel):
    """Response schema for one cart item."""

    id: int
    added_at: datetime
    movie: MovieResponse

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Response schema for the shopping cart."""

    id: int
    items: list[CartItemResponse]
    total_price: Decimal

    class Config:
        from_attributes = True
