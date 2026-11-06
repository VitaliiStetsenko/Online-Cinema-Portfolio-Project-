"""User profile service."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserProfile
from app.schemas.user import UserProfileCreate, UserProfileUpdate


async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[UserProfile]:
    """Get user profile by user id."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_user_profile(
    db: AsyncSession,
    user_id: int,
    data: UserProfileCreate
) -> UserProfile:
    """Create user profile."""
    profile = UserProfile(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        info=data.info
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_user_profile(
    db: AsyncSession,
    profile: UserProfile,
    data: UserProfileUpdate
) -> UserProfile:
    """Update user profile."""
    update_data = data.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_or_create_profile(
    db: AsyncSession,
    user_id: int
) -> UserProfile:
    """Get existing profile or create new one."""
    profile = await get_user_profile(db, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile
