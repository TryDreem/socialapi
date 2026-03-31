from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.schemas.notification import NotificationResponse
from app.models.user import User
from app.database import get_db
from app.schemas.pagination import PaginatedResponse
from app.services.notification_service import service
import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notification", tags=["notification"])




@router.get("", response_model=PaginatedResponse[NotificationResponse], status_code=200)
async def get_all_notifications(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Page size"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    return await service.get_all_notifications(page=page, page_size=page_size, current_user=current_user, db=db)


@router.patch("/{notification_id}/read", response_model=NotificationResponse, status_code=200)
async def read_notification(
        notification_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    result = await service.mark_as_read(notification_id=notification_id, current_user=current_user, db=db)
    if result == "Notification not found":
        raise HTTPException(status_code=404, detail="Notification not found")
    elif result == "Notification already read":
        raise HTTPException(status_code=409, detail="Notification already read")
    elif result == "forbidden":
        raise HTTPException(status_code=403, detail="User not allowed to change status of this notification")

    return result




