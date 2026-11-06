"""Pydantic schemas for authentication."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    """User registration schema."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class UserLogin(BaseModel):
    """User login schema."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class PasswordChange(BaseModel):
    """Password change schema."""

    old_password: str
    new_password: str = Field(min_length=8, max_length=100)


class PasswordResetRequest(BaseModel):
    """Password reset request schema."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Password reset schema."""

    token: str
    new_password: str = Field(min_length=8, max_length=100)


class ActivationResend(BaseModel):
    """Activation token resend schema."""

    email: EmailStr


class UserResponse(BaseModel):
    """User response schema."""

    id: int
    email: str
    is_active: bool
    created_at: datetime
    group_name: str

    class Config:
        from_attributes = True
