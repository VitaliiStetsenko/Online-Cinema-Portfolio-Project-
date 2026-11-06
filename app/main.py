"""Main FastAPI application."""

from fastapi import Depends, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.auth import router as auth_router
from app.api.cart import router as cart_router
from app.api.favorites import router as favorites_router
from app.api.interactions import router as interactions_router
from app.api.movies import catalog_router, router as movies_router
from app.api.users import router as users_router
from app.api.dependencies import get_current_active_user

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(auth_router, prefix="/api")
app.include_router(cart_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(interactions_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(movies_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")


@app.get("/docs", include_in_schema=False)
async def protected_swagger(_: object = Depends(get_current_active_user)):
    """Show Swagger only to authenticated users."""
    return get_swagger_ui_html(openapi_url="/openapi.json", title=f"{settings.app_title} docs")


@app.get("/openapi.json", include_in_schema=False)
async def protected_openapi(_: object = Depends(get_current_active_user)):
    """Return OpenAPI schema only to authenticated users."""
    return JSONResponse(get_openapi(title=settings.app_title, version=settings.app_version, routes=app.routes))


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Online Cinema API"}
