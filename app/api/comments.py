from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.pagination import PaginatedResponse
from app.schemas.comment import CommentResponse, CommentCreate
from app.models.user import User
from app.api.deps import get_current_user
from app.core.rate_limit import limiter

import logging

from app.services.comment_service import CommentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/post", tags=["comment"])

service = CommentService()

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
@limiter.limit("30/minute")
async def create_comment(
        request: Request,
        post_id: int,
        comment: CommentCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    result = await service.create_comment(post_id=post_id, comment=comment, current_user=current_user, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result




@router.get("/{post_id}/comments", response_model=PaginatedResponse[CommentResponse], status_code=200)
async def get_all_comments(
        post_id: int,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
):
    result = await service.get_all_comments(post_id=post_id, page=page, page_size=page_size, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
async def delete_comment(
        post_id: int,
        comment_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):

    result = await service.delete_comment(post_id=post_id, comment_id=comment_id, db=db, current_user=current_user)
    if result == "Comment not found":
        raise HTTPException(status_code=404, detail="Post not found")
    elif result == "forbidden":
        raise HTTPException(status_code=403, detail="You are not allowed to do this")
    return result





