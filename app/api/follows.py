from fastapi import APIRouter, Depends,Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.follow import FollowResponse, FollowersResponse
from app.models.user import User
from app.core.rate_limit import limiter
from app.api.deps import get_current_user
from app.services.follow_service import FollowService
from app.services.notification_service import service

import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["follow"])
service = FollowService()



@router.post("/{user_id}/follow", response_model=FollowResponse, status_code=201)
@limiter.limit("100/minute")
async def create_follow(
        request: Request,
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    result = await service.create_follow(user_id=user_id, db=db, current_user=current_user)
    if result == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    elif result == "User cannot follow himself":
        raise HTTPException(status_code=403, detail="User cannot follow himself")
    elif result == "User already followed":
        raise HTTPException(status_code=409, detail="User already followed")

    return result



@router.delete("/{user_id}/follow", status_code=204)
async def delete_follow(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
):
    result = await service.delete_follow(user_id=user_id, db=db, current_user=current_user)
    if result == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    elif result == "User cannot unfollow himself":
        raise HTTPException(status_code=403, detail="User cannot follow himself")
    elif result == "User not followed":
        raise HTTPException(status_code=404, detail="User not followed")

    return result

@router.get("/{user_id}/followers", response_model=FollowersResponse, status_code=200)
async def get_followers(
        user_id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await service.get_followers(user_id=user_id, db=db)
    if result == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    return result




