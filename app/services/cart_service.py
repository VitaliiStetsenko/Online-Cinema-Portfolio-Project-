"""Services for shopping cart management."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.models.movie import Movie


async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    """Get user cart or create if not exists."""
    cart = await db.scalar(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(
            selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.certification),
            selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.genres),
            selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.directors),
            selectinload(Cart.items).selectinload(CartItem.movie).selectinload(Movie.stars),
        )
    )
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart, ["items"])
    return cart


async def add_item(db: AsyncSession, user_id: int, movie_id: int) -> Cart:
    """Add movie to cart."""
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise ValueError("Movie not found")

    cart = await db.scalar(select(Cart).where(Cart.user_id == user_id))
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.flush()

    # Check if already in cart
    existing = await db.scalar(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.movie_id == movie_id))
    if existing:
        raise ValueError("Movie is already in cart")

    item = CartItem(cart_id=cart.id, movie_id=movie_id)
    db.add(item)
    await db.commit()

    return await get_or_create_cart(db, user_id)


async def remove_item(db: AsyncSession, user_id: int, movie_id: int) -> Cart:
    """Remove movie from cart."""
    cart = await db.scalar(select(Cart).where(Cart.user_id == user_id))
    if not cart:
        raise ValueError("Cart not found")

    item = await db.scalar(select(CartItem).where(CartItem.cart_id == cart.id, CartItem.movie_id == movie_id))
    if not item:
        raise ValueError("Movie not in cart")

    await db.delete(item)
    await db.commit()

    return await get_or_create_cart(db, user_id)


async def clear_cart(db: AsyncSession, user_id: int) -> None:
    """Remove all items from cart."""
    cart = await db.scalar(select(Cart).where(Cart.user_id == user_id).options(selectinload(Cart.items)))
    if cart:
        for item in cart.items:
            await db.delete(item)
        await db.commit()


def calculate_total(cart: Cart) -> Decimal:
    """Calculate total price of all items in cart."""
    return sum((item.movie.price or Decimal(0) for item in cart.items), Decimal(0))
