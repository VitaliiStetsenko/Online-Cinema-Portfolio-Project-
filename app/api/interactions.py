"""Ratings and comments API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.interaction import (
    CommentCreate,
    CommentReactionResponse,
    CommentResponse,
    CommentUpdate,
    MovieReactionResponse,
    NotificationResponse,
    MovieRatingSummary,
    RatingCreate,
    RatingResponse,
)
from app.services import interaction_service

router = APIRouter(tags=["Ratings and comments"])


@router.put("/movies/{movie_id}/rating", response_model=RatingResponse)
async def set_rating(
    movie_id: int,
    data: RatingCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Set or update the current user's 1-10 movie rating."""
    try:
        return await interaction_service.set_rating(db, current_user.id, movie_id, data.score)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/movies/{movie_id}/rating", response_model=MovieRatingSummary)
async def get_rating_summary(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Get average movie rating and the current user's score."""
    try:
        return await interaction_service.get_rating_summary(db, current_user.id, movie_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/movies/{movie_id}/comments", response_model=CommentResponse, status_code=201)
async def create_comment(
    movie_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Write a comment for a movie."""
    try:
        comment = await interaction_service.create_comment(
            db, current_user.id, movie_id, data.text, data.parent_comment_id
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return interaction_service.serialize_comment(comment, current_user.id)


@router.get("/movies/{movie_id}/comments", response_model=list[CommentResponse])
async def list_comments(
    movie_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List comments for a movie."""
    comments = await interaction_service.list_comments(db, movie_id)
    return [interaction_service.serialize_comment(comment, current_user.id) for comment in comments]


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's comment."""
    comment = await interaction_service.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can update only your comments")
    updated = await interaction_service.update_comment(db, comment, data.text)
    return interaction_service.serialize_comment(updated, current_user.id)


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete the current user's comment."""
    comment = await interaction_service.get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can delete only your comments")
    await interaction_service.delete_comment(db, comment)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/comments/{comment_id}/reaction", response_model=CommentReactionResponse)
async def set_comment_reaction(
    comment_id: int,
    is_like: bool,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Like or dislike a comment."""
    try:
        comment = await interaction_service.set_comment_reaction(db, current_user.id, comment_id, is_like)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    data = interaction_service.serialize_comment(comment, current_user.id)
    return {
        "comment_id": comment.id,
        "is_like": is_like,
        "likes_count": data["likes_count"],
        "dislikes_count": data["dislikes_count"],
    }


@router.put("/movies/{movie_id}/reaction", response_model=MovieReactionResponse)
async def set_movie_reaction(
    movie_id: int,
    is_like: bool,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Like or dislike a movie."""
    try:
        return await interaction_service.set_movie_reaction(db, current_user.id, movie_id, is_like)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    """List notifications about comment replies and reactions."""
    return await interaction_service.list_notifications(db, current_user.id)


@router.patch("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark one notification as read."""
    notification = await interaction_service.mark_notification_read(db, current_user.id, notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification
