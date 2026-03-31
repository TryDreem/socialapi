from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.schemas.pagination import PaginatedResponse

from app.models import Post
from app.schemas.comment import CommentResponse, CommentCreate
from app.models.user import User
from app.models.comment import Comment
import logging
from app.services.notification_service import service

logger = logging.getLogger(__name__)



class CommentService:
    async def create_comment(self, post_id: int, comment: CommentCreate, current_user: User, db: AsyncSession):

        post = await db.get(Post, post_id)

        if not post:
            logger.info(f"Post {post_id} not found")
            return None

        db_comment = Comment(
            body=comment.body,
            user_id=current_user.id,
            post_id=post_id,
        )

        db.add(db_comment)

        logger.info(f"Comment created by {current_user.id}")

        await db.commit()
        await db.refresh(db_comment)
        await service.create_notification(
            user_id = post.user_id,
            actor_id = current_user.id,
            type = "comment",
            post_id = post.id,
        )

        return CommentResponse.model_validate(db_comment)


    async def get_all_comments(self, post_id: int, page: int, page_size: int, db: AsyncSession):

        logger.info(f"📋 Getting comments for post {post_id} (page={page}, page_size={page_size})")

        post = await db.get(Post, post_id)

        if not post:
            logger.info(f"Post {post_id} not found")
            return None

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

    async def delete_comment(self, post_id: int, comment_id: int, db: AsyncSession, current_user: User):

        comment = await db.get(Comment, comment_id)

        if not comment:
            logger.warning(f"No comment for post {post_id}")
            return "Comment not found"

        if comment.user_id != current_user.id:
            logger.warning(f"User {current_user.id} tried to delete post {comment_id} of user {comment.user_id}")
            return "forbidden"

        await db.delete(comment)
        await db.commit()

        logger.info(f"Comment deleted by {current_user.id}")

        return