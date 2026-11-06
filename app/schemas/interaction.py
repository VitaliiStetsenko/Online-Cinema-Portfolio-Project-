"""Pydantic schemas for ratings and comments."""

from datetime import datetime

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """Input schema for a movie rating."""

    score: int = Field(ge=1, le=10)


class RatingResponse(BaseModel):
    """Response schema for a movie rating."""

    id: int
    movie_id: int
    score: int
    created_at: datetime

    class Config:
        from_attributes = True


class MovieRatingSummary(BaseModel):
    """Aggregate rating information for one movie."""

    movie_id: int
    average_score: float | None
    ratings_count: int
    user_score: int | None


class CommentCreate(BaseModel):
    """Input schema for a movie comment."""

    text: str = Field(min_length=1, max_length=5000)


class CommentUpdate(BaseModel):
    """Input schema for updating a movie comment."""

    text: str = Field(min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Response schema for a movie comment."""

    id: int
    user_id: int
    movie_id: int
    text: str
    created_at: datetime
    updated_at: datetime
    likes_count: int
    dislikes_count: int
    current_user_reaction: bool | None


class CommentReactionResponse(BaseModel):
    """Response schema for a comment reaction."""

    comment_id: int
    is_like: bool
    likes_count: int
    dislikes_count: int
