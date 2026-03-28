from fastapi import APIRouter, HTTPException, Depends,Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from app.models import Post, Like
from app.schemas.like import LikeResponse, LikeCountResponse
from app.models.user import User
from app.core.rate_limit import limiter
from app.api.deps import get_current_user
from app.services.like_service import LikeService

import logging

from app.services.post_service import PostService

logger = logging.getLogger(__name__)
service = LikeService()

router = APIRouter(prefix="/post", tags=["like"])


@router.post("/{post_id}/like", response_model=LikeResponse, status_code=201)
@limiter.limit("1/minute")
async def post_like(
        request: Request,
        post_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
   result = await service.post_like(db=db, post_id=post_id, current_user=current_user)
   if not result:
       raise HTTPException(status_code=404, detail="Post not found")
   elif result == "post already exists":
       raise HTTPException(status_code=409, detail="Post already exists")
   return result


@router.delete("/{post_id}/like",status_code=204)
async def delete_like(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
   result = await service.delete_like(post_id=post_id, current_user=current_user, db=db)
   if result == "post not found":
       raise HTTPException(status_code=404, detail="Post not found")
   elif result == "like not found":
       raise HTTPException(status_code=404, detail="Like not found")
   return result


@router.get("/{post_id}/like", response_model=LikeCountResponse)
async def get_likes_count(
        post_id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await service.get_likes_count(post_id=post_id, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    return result


