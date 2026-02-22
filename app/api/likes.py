from fastapi import APIRouter, HTTPException, Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models import Post, Like
from app.schemas.like import LikeResponse, LikeCountResponse
from app.models.user import User
from app.core.rate_limit import limiter
from app.api.deps import get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/post", tags=["like"])


@router.post("/{post_id}/like", response_model=LikeResponse, status_code=201)
@limiter.limit("1/minute")
async def post_like(
        request: Request,
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    post = await db.get(Post, post_id)

    if not post:
        logger.warning(f"post {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    db_like = Like(
        post_id=post_id,
        user_id=current_user.id
    )

    try:
        db.add(db_like)
        await db.commit()
        await db.refresh(db_like)

    except IntegrityError:
        await db.rollback()
        logger.warning(f"like to post {post_id} already exists")
        raise HTTPException(status_code=409, detail="Post already liked")


    logger.info(f"post {post_id} liked")

    return LikeResponse.model_validate(db_like)


@router.delete("/{post_id}/like",status_code=204)
async def delete_like(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    post = await db.get(Post, post_id)

    if not post:
        logger.warning(f"post {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")


    query = select(Like).where(
        Like.user_id == current_user.id,
        Like.post_id == post.id
    )
    result = await db.execute(query)
    like = result.scalar_one_or_none()

    if not like:
        logger.warning(f"like {post_id} not found")
        raise HTTPException(status_code=404, detail="like not found")


    await db.delete(like)
    await db.commit()

    logger.info(f"post {post_id} unliked by {current_user.id}")

    return


@router.get("/{post_id}/like", response_model=LikeCountResponse)
async def get_likes_count(
        post_id: int,
        db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)

    if not post:
        logger.warning(f"post {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    query = select(func.count(Like.id)).where(Like.post_id == post_id)
    result = await db.execute(query)
    count = result.scalar()

    return LikeCountResponse(post_id=post_id, count=count)


