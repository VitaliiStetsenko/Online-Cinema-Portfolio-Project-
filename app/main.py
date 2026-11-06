"""Main FastAPI application."""
from fastapi import FastAPI
from app.core.config import settings

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    debug=settings.debug
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Online Cinema API"}
