"""Cleanup tasks for Celery Beat."""

from datetime import datetime
from sqlalchemy import select
from app.tasks.celery_app import celery_app
from app.db.session import async_session_maker
from app.models.user import ActivationToken, PasswordResetToken, RefreshToken


@celery_app.task
def cleanup_expired_tokens():
    """Remove expired tokens from database."""
    import asyncio

    asyncio.run(_cleanup_expired_tokens())


async def _cleanup_expired_tokens():
    """Async cleanup of expired tokens."""
    async with async_session_maker() as db:
        now = datetime.utcnow()

        # Delete expired activation tokens
        result = await db.execute(select(ActivationToken).where(ActivationToken.expires_at < now))
        expired_activation_tokens = result.scalars().all()
        for token in expired_activation_tokens:
            await db.delete(token)

        # Delete expired password reset tokens
        result = await db.execute(select(PasswordResetToken).where(PasswordResetToken.expires_at < now))
        expired_reset_tokens = result.scalars().all()
        for token in expired_reset_tokens:
            await db.delete(token)

        # Delete expired refresh tokens
        result = await db.execute(select(RefreshToken).where(RefreshToken.expires_at < now))
        expired_refresh_tokens = result.scalars().all()
        for token in expired_refresh_tokens:
            await db.delete(token)

        await db.commit()

        total_deleted = len(expired_activation_tokens) + len(expired_reset_tokens) + len(expired_refresh_tokens)
        print(f"Deleted {total_deleted} expired tokens")
