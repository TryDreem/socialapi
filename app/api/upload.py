import os

from fastapi import APIRouter, HTTPException, Depends, Request, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.post import PostResponse, PostCreate, PostUpdate, PostSortBy
from app.models.user import User
from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.schemas.pagination import PaginatedResponse
from app.services.storage_service import StorageService
import logging



logger = logging.getLogger(__name__)
service = StorageService()
MAX_SIZE = 5 * 1024 * 1024  # 5 MB

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/image", status_code=200)
@limiter.limit("10/hour")
async def upload_image(
        request: Request,
        file: UploadFile,
        current_user: User = Depends(get_current_user),
)-> str:
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=400, detail="This image type is not supported.")

    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Maximum allowed file resolution is 5 MB")


    return await service.upload_file(file=file, user_id=current_user.id)
