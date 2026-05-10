from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import comment_repository
from app.schemas.pagination import PaginatedResponse

from app.models import Post
from app.schemas.comment import CommentResponse, CommentCreate
from app.models.user import User
from app.models.comment import Comment
import logging
from app.services.notification_service import service
from app.repositories.comment_repository import comment_repository

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

        logger.info(f"Comment created by {current_user.id}")

        await comment_repository.create(db, db_comment)

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

        total = await comment_repository.get_total_count(db, post_id)
        comments = await comment_repository.get_all(db, post_id, page_size, offset)

        comments_data = [CommentResponse.model_validate(c) for c in comments]

        total_pages = (total + page_size - 1) // page_size

        return PaginatedResponse(
            items=comments_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def delete_comment(self, post_id: int, comment_id: User, db: AsyncSession, current_user: User):

        comment = await db.get(Comment, comment_id)

        if not comment:
            logger.warning(f"No comment for post {post_id}")
            return "Comment not found"

        if comment.user_id != current_user.id:
            logger.warning(f"User {current_user.id} tried to delete post {comment_id} of user {comment.user_id}")
            return "forbidden"

        await comment_repository.delete(db, comment)

        logger.info(f"Comment deleted by {current_user.id}")

        return