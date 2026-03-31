from celery import Celery
from app.config import settings


celery_app = Celery(
    "socialapi",
    broker=settings.REDIS_URL + "/1",
    backend=settings.REDIS_URL + "/2",
    include=["app.tasks.email", "app.tasks.notifications"]
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="UTC",
)