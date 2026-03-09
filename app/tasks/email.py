from app.celery_app import celery_app
import httpx
import logging
from app.config import settings
from app.core.utils import mask_email
import asyncio
from app.services.email import send_confirmation_email

logger = logging.getLogger(__name__)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=5
)

def send_confirmation_email_task(self, email: str, confirmation_url: str) -> bool:
    result = asyncio.run(send_confirmation_email(email, confirmation_url))
    if not result:
        logger.error("Failed to send confirmation email")
        raise self.retry()
    return result
