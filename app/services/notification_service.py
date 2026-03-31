import logging

from app.database import AsyncSessionLocal
from app.models import Notification
from app.schemas.notification import NotificationResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.models.user import User
from app.schemas.pagination import PaginatedResponse
from app.core.websocket_manager import manager

logger = logging.getLogger(__name__)


class NotificationService:
    async def create_notification(self, user_id, actor_id, type, post_id):
        logger.info(f"Creating notification for user {user_id} with type {type}")

        try:
            async with AsyncSessionLocal() as db:

                notification = Notification(
                    user_id=user_id,
                    actor_id=actor_id,
                    type=type,
                    post_id=post_id,
                )

                db.add(notification)
                await db.commit()
                await db.refresh(notification)
                await manager.send_to_user(notification.user_id, message={
                    "type": notification.type,
                    "actor_id": notification.actor_id,
                    "post_id": notification.post_id,
                    }
                )

                return True

        except Exception as e:
            logger.warning(f"Failed to create notification for user {user_id} with type {type}: {e}")
            return False

    async def get_all_notifications(self, page: int, page_size: int, current_user: User, db: AsyncSession):
        logger.info(f"Getting all notifications for user {current_user.id}")

        count_query = (
            select(func.count(Notification.id))
            .where(Notification.user_id == current_user.id)
        )

        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size

        query = (
            select(Notification)
            .where(Notification.user_id == current_user.id)
            .order_by(desc(Notification.created_at))
            .limit(page_size)
            .offset(offset)
        )

        result = await db.execute(query)

        """
        raw_list = result.scalars().all()
        notifications = []
        for n in raw_list:
        validated_n = NotificationResponse.model_validate(n)  - converting to Pydantic scheme each object (notification with full info)
        notifications.append(validated_n)
        """
        notifications = [NotificationResponse.model_validate(n) for n in result.scalars().all()]

        total_pages = (total + page_size - 1) // page_size

        response = PaginatedResponse(
            items=notifications,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

        return response


    async def mark_as_read(self, notification_id: int, current_user: User, db: AsyncSession):
        logger.info(f"Marking notification for user {current_user.id} with id {notification_id} as read")

        notification = await db.get(Notification, notification_id)

        if not notification:
            logger.warning(f"Notification with id {notification_id} was not found")
            return "Notification not found"

        if notification.is_read == True:
            logger.warning(f"Notification with id {notification_id} was already read")
            return "Notification already read"

        if notification.user_id != current_user.id:
            logger.warning(f"User {current_user.id} tried to read notification {notification_id} of user {notification.user_id}")
            return "forbidden"

        notification.is_read = True

        await db.commit()
        await db.refresh(notification)

        return NotificationResponse.model_validate(notification)

service = NotificationService()

