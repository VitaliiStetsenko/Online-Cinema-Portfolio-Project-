"""User profile service."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserGroup, UserProfile
from app.schemas.user import UserProfileCreate, UserProfileUpdate


async def get_user_profile(db: AsyncSession, user_id: int) -> Optional[UserProfile]:
    """Get user profile by user id."""
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    return result.scalar_one_or_none()


async def create_user_profile(db: AsyncSession, user_id: int, data: UserProfileCreate) -> UserProfile:
    """Create user profile."""
    profile = UserProfile(
        user_id=user_id,
        first_name=data.first_name,
        last_name=data.last_name,
        gender=data.gender,
        date_of_birth=data.date_of_birth,
        info=data.info,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_user_profile(db: AsyncSession, profile: UserProfile, data: UserProfileUpdate) -> UserProfile:
    """Update user profile."""
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile


async def get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfile:
    """Get existing profile or create new one."""
    profile = await get_user_profile(db, user_id)
    if not profile:
        profile = UserProfile(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def list_users(db: AsyncSession) -> list[User]:
    """List users for administrator management."""
    result = await db.execute(select(User).options(selectinload(User.group)).order_by(User.id))
    return list(result.scalars())


async def update_user_by_admin(
    db: AsyncSession, user: User, group_name: str | None, is_active: bool | None
) -> User:
    """Change a user's role or activation status as an administrator."""
    if group_name is not None:
        group = await db.scalar(select(UserGroup).where(UserGroup.name == group_name))
        if not group:
            raise ValueError("User group not found")
        user.group_id = group.id
    if is_active is not None:
        user.is_active = is_active
    await db.commit()
    await db.refresh(user, ["group"])
    return user
