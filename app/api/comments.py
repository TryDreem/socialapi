from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, desc, func
from app.schemas.pagination import PaginatedResponse

from app.models import Post
from app.schemas.comment import CommentResponse, CommentCreate, CommentsResponse
from app.models.user import User
from app.models.comment import Comment
from app.api.deps import get_current_user
from app.core.rate_limit import limiter

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/post", tags=["comment"])



@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
@limiter.limit("30/minute")
async def create_comment(
        request: Request,
        post_id: int,
        comment: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):

    post = await db.get(Post, post_id)

    if not post:
        logger.info(f"Post {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    db_comment = Comment(
        body=comment.body,
        user_id=current_user.id,
        post_id=post_id,
    )

    db.add(db_comment)

    logger.info(f"Comment created by {current_user.id}")

    await db.commit()
    await db.refresh(db_comment)

    return CommentResponse.model_validate(db_comment)



@router.get("/{post_id}/comments", response_model=PaginatedResponse[CommentResponse], status_code=200)
async def get_all_comments(
        post_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"📋 Getting comments for post {post_id} (page={page}, page_size={page_size})")

    post = await db.get(Post, post_id)

    if not post:
        logger.info(f"Post {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    offset = (page - 1) * page_size

    count_query = select(func.count(Comment.id)).where(Comment.post_id==post_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = (select(Comment)
    .where(Comment.post_id==post_id)
    .order_by(Comment.created_at)
    .limit(page_size)
    .offset(offset)
    )

    result = await db.execute(query)
    comments = result.scalars().all()

    comments_data = [CommentResponse.model_validate(c) for c in comments]

    total_pages = (total + page_size - 1) // page_size

    return PaginatedResponse(
        items=comments_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )



@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
        post_id: int,
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    comment = await db.get(Comment, comment_id)

    if not comment:
        logger.warning(f"No comment for post {post_id}")
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.id:
        logger.warning(f"User {current_user.id} tried to delete post {comment_id} of user {comment.user_id}")
        raise HTTPException(status_code=403, detail="You are not authorized to perform this action")

    await db.delete(comment)
    await db.commit()

    logger.info(f"Comment deleted by {current_user.id}")

    return






