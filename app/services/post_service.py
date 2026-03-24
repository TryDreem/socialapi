from sqlalchemy.ext.asyncio import AsyncSession
from app.api.posts import PostSortBy
from sqlalchemy import select, desc, func, text
import json
from app.models import Like
from app.schemas.post import PostResponse, PostCreate
from app.models.user import User
from app.models.post import Post

from app.schemas.pagination import PaginatedResponse
from app.core.redis import cache_get, cache_set, cache_pattern_delete
from fastapi.encoders import jsonable_encoder


import logging

logger = logging.getLogger(__name__)


class PostService:
    async def create_post(self, post: PostCreate, current_user: User, db: AsyncSession):
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



    async def search(self, q: str, page: int, page_size: int, db: AsyncSession, sort_by: PostSortBy):

        logger.info(f"Searching posts with query: {q}")

        cache_key = f"cache:search:{q}:page{page}:page_size:{page_size}:sort_by:{sort_by}"
        cached = await cache_get(cache_key)
        if cached:
            logger.info(f"Searched posts found in cache")
            return json.loads(cached)

        count_query = (
            select(func.count(Post.id))
            .where(Post.body.like(f"%{q}%"))
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()


        offset = (page - 1) * page_size

        if sort_by == PostSortBy.newest:
            order_clause = desc(Post.created_at)
        elif sort_by == PostSortBy.oldest:
            order_clause = Post.created_at
        else:
            order_clause = desc(text("likes_count"))

        query = (
            select(Post, func.count(Like.id).label("likes_count"))
            .where(Post.body.ilike(f"%{q}%"))
            .outerjoin(Like, Post.id == Like.post_id)
            .group_by(Post.id)
            .order_by(order_clause)
            .limit(page_size)
            .offset(offset)
        )

        result = await db.execute(query)
        rows = result.all()

        posts_data = []
        for post, likes_count in rows:
            post_dict = {
                "id": post.id,
                "body": post.body,
                "user_id": post.user_id,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "likes_count": likes_count or 0
            }
            posts_data.append(post_dict)

        total_pages = (total + page_size - 1) // page_size

        response = PaginatedResponse(
            items=posts_data,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

        await cache_set(cache_key, json.dumps(jsonable_encoder(response)))

        return response
