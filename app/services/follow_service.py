from fastapi import APIRouter, HTTPException, Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.models import Follow
from app.schemas.follow import FollowResponse, FollowersResponse
from app.models.user import User
from app.api.deps import get_current_user
from app.services.notification_service import service

import logging

logger = logging.getLogger(__name__)


class FollowService:
    async def create_follow(self, user_id: int, db: AsyncSession,current_user: User):
        user = await db.get(User, user_id)

        if not user:
            logger.warning(f"User {user_id} not found.")
            return "User not found"

        if current_user.id == user.id:
            logger.warning(f"User cannot follow himself")
            return "User cannot follow himself"

        db_follow = Follow(
            follower_id=current_user.id,
            following_id=user_id,
        )

        try:
            db.add(db_follow)
            await db.commit()
            await db.refresh(db_follow)
            await service.create_notification(
                user_id=user_id,
                actor_id=current_user.id,
                type = "follow",
                post_id=None
            )

        except IntegrityError:
            logger.warning(f"User {user_id} already followed")
            await db.rollback()
            return "User already followed"
        logger.info(f"User {user_id} followed by {current_user.id}")

        return FollowResponse.model_validate(db_follow)


    async def delete_follow(self, user_id: int, db: AsyncSession, current_user: User):
        user = await db.get(User, user_id)

        if not user:
            logger.warning(f"User {user_id} not found.")
            return "User not found"
        if current_user.id == user.id:
            logger.warning(f"User cannot unfollow himself")
            return "User cannot unfollow himself"

        query = select(Follow).where(Follow.following_id == user_id, Follow.follower_id == current_user.id)
        result = await db.execute(query)
        follow = result.scalar_one_or_none()
        if not follow:
            logger.warning(f"User {user_id} is not followed")
            return "User not followed"
        await db.delete(follow)
        await db.commit()

        logger.info(f"User {user_id} unfollowed by {current_user.id}")

        return


    async def get_followers(self, user_id: int, db: AsyncSession):
        user = await db.get(User, user_id)
        if not user:
            logger.warning(f"User {user_id} not found.")
            return "User not found"

        query = select(User).join(Follow, Follow.follower_id == User.id).where(Follow.following_id == user_id)
        result = await db.execute(query)
        followers = result.scalars().all()

        return FollowersResponse(followers=followers)

