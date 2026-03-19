from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from sqlalchemy import select, desc, func
from enum import Enum
import json
from app.models import Like
from app.schemas.post import PostResponse, PostCreate, PostsResponse, PostUpdate
from app.models.user import User
from app.models.post import Post
from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.schemas.pagination import PaginatedResponse
from app.core.redis import cache_get, cache_set, cache_pattern_delete
from fastapi.encoders import jsonable_encoder


import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/post", tags=["post"])


class PostSortBy(str, Enum):
    newest = "newest"
    oldest = "oldest"
    most_liked = "most_liked"




@router.post("", response_model=PostResponse, status_code=201)
@limiter.limit("20/minute")
async def create_post(
        request: Request,
        post: PostCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):

    db_post = Post(
        body=post.body,
        user_id=current_user.id,
    )

    db.add(db_post)

    logger.info(f"Post created by {current_user.id}")

    await db.commit()
    await db.refresh(db_post)

    await cache_pattern_delete("cache:posts:*")
    logger.info(f"Cache pattern cleared in Redis")

    return PostResponse.model_validate(db_post)

@router.get("", response_model=PaginatedResponse[PostResponse], status_code=200)
async def get_all_posts(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Page size"),
        sort_by: PostSortBy = Query(PostSortBy.most_liked),
        db: AsyncSession = Depends(get_db)
        #ge greater or equal (>=1)
):
    logger.info(f"Getting posts (page={page}, page_size={page_size})")

    cache_key = f"cache:posts:page:{page}:page_size:{page_size}:sort_by:{sort_by}"

    cached_posts = await cache_get(cache_key)
    if cached_posts:
        logger.info(f"Found cached posts (page={page}, page_size={page_size})")
        return json.loads(cached_posts)

    count_query = select(func.count(Post.id))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size


    if sort_by == PostSortBy.newest:
        order_clause = desc(Post.created_at)
    elif sort_by == PostSortBy.oldest:
        order_clause = Post.created_at
    else:
        order_clause = desc("likes_count")


    query = (
        select(Post, func.count(Like.id).label("likes_count")) #COUNT(likes.id) AS likes_count
        .outerjoin(Like, Post.id == Like.post_id)
        .group_by(Post.id)
        .order_by(order_clause)
        .limit(page_size)
        .offset(offset)
    )
    result = await db.execute(query)
    rows = result.all()

    post_data = []
    for post, likes_count in rows:
        post_dict = {
            "id": post.id,
            "body": post.body,
            "user_id": post.user_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "likes_count": likes_count or 0  # 0 если None
        }
        post_data.append(post_dict)

    total_pages = (total + page_size - 1) // page_size

    response = PaginatedResponse(
        items=post_data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )

    # jsonable_encoder(response):
    # "created_at": datetime(2026, 3, 8, 22, 13, 50) -> "items": [{"id": 1, "created_at": "2026-03-08T22:13:50"
    # json.dumps(...)  turns it into string
    await cache_set(cache_key, json.dumps(jsonable_encoder(response)))
    logger.info(f"Posts were saved to cache Redis")

    return response

@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Getting post with id {post_id}")

    cache_key = f"cache:posts:post:{post_id}"
    cached = await cache_get(cache_key)

    if cached:
        logger.info(f"Found cached post with id {post_id}")
        return json.loads(cached)


    query = (
        select(Post, func.count(Like.id).label("likes_count")) #COUNT(likes.id) AS likes_count
        .outerjoin(Like, Post.id == Like.post_id)
        .where(Post.id == post_id)
        .group_by(Post.id)
    )

    result = await db.execute(query)
    row = result.first()

    if not row:
        logger.warning(f"Post with id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    post, likes_count = row

    post_dict = {
        "id": post.id,
        "body": post.body,
        "user_id": post.user_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "likes_count": likes_count or 0
    }

    response = PostResponse(**post_dict)

    logger.info(f"Post was saved to Redis")
    await cache_set(cache_key, json.dumps(jsonable_encoder(response)))

    return response


@router.delete("/{post_id}", status_code=204)
async def delete_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Deleting post with id {post_id}")

    query = select(Post).where(Post.id == post_id)
    result = await db.execute(query)
    post = result.scalar_one_or_none()
    if not post:
        logger.warning(f"Post with id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        logger.warning(f"User {current_user.id} tried to delete post {post_id} of user {post.user_id}")
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    await db.delete(post)
    await db.commit()

    logger.info(f"Deleted post with id {post_id}")

    await cache_pattern_delete("cache:posts:*")
    logger.info(f"Cache pattern deleted")

    return


@router.patch("/{post_id}", response_model=PostResponse, status_code=200)
async def update_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Getting post with id {post_id}")

    post = await db.get(Post, post_id)

    if not post:
        logger.warning(f"Post with id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        logger.warning("User not allowed to update post")
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    updates = post_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(status_code=404, detail="No fields to update")

    for key, value in updates.items():
        setattr(post, key, value)

    post.updated_at = datetime.now()

    await db.commit()
    await db.refresh(post)

    await cache_pattern_delete("cache:posts:*")
    logger.info(f"Cache pattern cleared in Redis")


    return PostResponse.model_validate(post)


