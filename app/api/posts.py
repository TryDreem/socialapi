from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.post import PostResponse, PostCreate, PostUpdate, PostSortBy
from app.models.user import User
from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.schemas.pagination import PaginatedResponse
from app.services.post_service import PostService
import logging



logger = logging.getLogger(__name__)
service = PostService()

router = APIRouter(prefix="/post", tags=["post"])
feed_router = APIRouter(prefix="/feed", tags=["feed"])


@router.post("", response_model=PostResponse, status_code=201)
@limiter.limit("20/minute")
async def create_post(
        request: Request,
        post: PostCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    return await service.create_post(post=post, current_user=current_user, db=db)


@router.get("/search", response_model=PaginatedResponse[PostResponse], status_code=200)
async def search_posts(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        q: str = Query(..., min_length=1),
        sort_by: PostSortBy = Query(PostSortBy.most_liked),
        db: AsyncSession = Depends(get_db)
):
    return await service.search(q=q, page=page, page_size=page_size, db=db, sort_by=sort_by)


@router.get("", response_model=PaginatedResponse[PostResponse], status_code=200)
async def get_all_posts(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Page size"),
        sort_by: PostSortBy = Query(PostSortBy.most_liked),
        db: AsyncSession = Depends(get_db)
        #ge greater or equal (>=1)
):
    return await service.get_all_posts(page=page, page_size=page_size, sort_by=sort_by, db=db)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
):
    result = await service.get_post(post_id=post_id, db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@router.delete("/{post_id}", status_code=204)
async def delete_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    result = await service.delete_post(post_id=post_id,current_user=current_user,db=db)
    if result == "Post not found":
        raise HTTPException(status_code=404, detail="Post not found")
    elif result == "forbidden":
        raise HTTPException(status_code=403, detail="You are not allowed delete this post")
    return result


@router.patch("/{post_id}", response_model=PostResponse, status_code=200)
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    result = await service.update_post(post_id=post_id,post_data=post_data,current_user=current_user,db=db)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    elif result == "forbidden":
        raise HTTPException(status_code=403, detail="You are not allowed update this post")
    return result


@feed_router.get("",response_model=PaginatedResponse[PostResponse], status_code=200)
async def get_feed(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    return await service.get_feed(page=page, page_size=page_size, current_user=current_user, db=db)





