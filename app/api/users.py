"""User profile API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserProfileCreate, UserProfileUpdate, UserProfileResponse, UserFullResponse
from app.services import user_service
from app.api.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserFullResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile."""
    profile = await user_service.get_user_profile(db, current_user.id)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "group_name": current_user.group.name,
        "profile": profile
    }


@router.post("/me/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_my_profile(
    data: UserProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Create user profile."""
    existing_profile = await user_service.get_user_profile(db, current_user.id)
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists"
        )
    
    profile = await user_service.create_user_profile(db, current_user.id, data)
    return profile


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_my_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    profile = await user_service.get_or_create_profile(db, current_user.id)
    updated_profile = await user_service.update_user_profile(db, profile, data)
    return updated_profile
