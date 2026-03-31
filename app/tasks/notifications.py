from typing import Optional
from app.services.notification_service import service
from app.celery_app import celery_app
import logging
import asyncio


logger = logging.getLogger(__name__)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5
)

def create_notification_task(
        self,
        user_id: int,
        actor_id: int,
        type: str,
        post_id: Optional[int]
):
    result = asyncio.run(service.create_notification(user_id=user_id,actor_id=actor_id,type=type,post_id=post_id))
    if not result:
        raise self.retry()
    return result
