"""Main FastAPI application."""
from fastapi import FastAPI
from app.core.config import settings
from app.api.auth import router as auth_router

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug
)

app.include_router(auth_router, prefix="/api")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Online Cinema API"}
