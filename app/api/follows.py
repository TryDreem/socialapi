from fastapi import APIRouter, HTTPException, Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models import Follow
from app.schemas.follow import FollowResponse, FollowersResponse
from app.models.user import User
from app.core.rate_limit import limiter
from app.api.deps import get_current_user

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["follow"])


@router.post("/{user_id}/follow", response_model=FollowResponse, status_code=201)
@limiter.limit("100/minute")
async def create_follow(
        request: Request,
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)

    if not user:
        logger.warning(f"User {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user.id:
        logger.warning(f"User cannot follow himself")
        raise HTTPException(status_code=403, detail="You cannot follow yourself")

    db_follow = Follow(
        follower_id=current_user.id,
        following_id=user_id,
    )

    try:
        db.add(db_follow)
        await db.commit()
        await db.refresh(db_follow)

    except IntegrityError:
        logger.warning(f"User {user_id} already followed")
        await db.rollback()
        raise HTTPException(status_code=409, detail="User already followed")

    logger.info(f"User {user_id} followed by {current_user.id}")

    return FollowResponse.model_validate(db_follow)


@router.delete("/{user_id}/follow", status_code=204)
async def delete_follow(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    user = await db.get(User, user_id)

    if not user:
        logger.warning(f"User {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.id == user.id:
        logger.warning(f"User cannot unfollow himself")
        raise HTTPException(status_code=403, detail="You cannot unfollow yourself")


    query = select(Follow).where(Follow.following_id == user_id, Follow.follower_id == current_user.id)
    result = await db.execute(query)
    follow = result.scalar_one_or_none()
    if not follow:
        logger.warning(f"User {user_id} is not followed")
        raise HTTPException(status_code=404, detail="User is not followed")

    await db.delete(follow)
    await db.commit()

    logger.info(f"User {user_id} unfollowed by {current_user.id}")

    return


@router.get("/{user_id}/followers", response_model=FollowersResponse, status_code=200)
async def get_followers(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, user_id)
    if not user:
        logger.warning(f"User {user_id} not found.")
        raise HTTPException(status_code=404, detail="User not found")

    query = select(User).join(Follow, Follow.follower_id == User.id).where(Follow.following_id == user_id)
    result = await db.execute(query)
    followers = result.scalars().all()

    if not followers:
        logger.warning(f"User {user_id} is not followed")


    return FollowersResponse(followers=followers)





