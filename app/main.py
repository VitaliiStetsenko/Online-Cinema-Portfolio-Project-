"""Main FastAPI application."""
from fastapi import FastAPI
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.cart import router as cart_router
from app.api.favorites import router as favorites_router
from app.api.interactions import router as interactions_router
from app.api.movies import catalog_router, router as movies_router
from app.api.users import router as users_router

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(auth_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(movies_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Online Cinema API"}
