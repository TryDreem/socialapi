from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models import Post, Like
from app.schemas.like import LikeResponse, LikeCountResponse
from app.models.user import User


import logging

logger = logging.getLogger(__name__)

class LikeService:
    async def post_like(self, post_id: int, db: AsyncSession, current_user: User):
        post = await db.get(Post, post_id)

        if not post:
            logger.warning(f"post {post_id} not found")
            return None

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
            return "post already exists"

        logger.info(f"post {post_id} liked")

        return LikeResponse.model_validate(db_like)


    async def delete_like(self, post_id: int, current_user: User, db: AsyncSession):
        post = await db.get(Post, post_id)

        if not post:
            logger.warning(f"post {post_id} not found")
            return "post not found"

        query = select(Like).where(
            Like.user_id == current_user.id,
            Like.post_id == post.id
        )
        result = await db.execute(query)
        like = result.scalar_one_or_none()

        if not like:
            logger.warning(f"like {post_id} not found")
            return "like not found"


        await db.delete(like)
        await db.commit()

        logger.info(f"post {post_id} unliked by {current_user.id}")

        return


    async def get_likes_count(self, post_id: int, db: AsyncSession):
        post = await db.get(Post, post_id)

        if not post:
            logger.warning(f"post {post_id} not found")
            return None

        query = select(func.count(Like.id)).where(Like.post_id == post_id)
        result = await db.execute(query)
        count = result.scalar()

        return LikeCountResponse(post_id=post_id, count=count)


