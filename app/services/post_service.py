from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, text, case
from app.models import Like
from app.schemas.post import PostResponse, PostCreate, PostUpdate, PostSortBy
from app.models.user import User
from app.models.post import Post
from app.models.follow import Follow
from app.models.comment import Comment

from app.schemas.pagination import PaginatedResponse
from app.core.redis import cache_get, cache_set, cache_pattern_delete
from fastapi.encoders import jsonable_encoder
from app.repositories.post_repository import post_repository

import json
import logging

logger = logging.getLogger(__name__)


class PostService:
    async def create_post(self, post: PostCreate, current_user: User, db: AsyncSession):
        db_post = Post(
            body=post.body,
            user_id=current_user.id,
        )

        await post_repository.create(db, db_post)

        logger.info(f"Post created by {current_user.id}")

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

        total = await post_repository.count_search(db, q)

        offset = (page - 1) * page_size

        if sort_by == PostSortBy.newest:
            order_clause = desc(Post.created_at)
        elif sort_by == PostSortBy.oldest:
            order_clause = Post.created_at
        else:
            order_clause = desc(text("likes_count"))

        rows = await post_repository.search(db, order_clause, page_size, offset, q)

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


    async def get_all_posts(self, page: int, page_size: int, sort_by: PostSortBy, db: AsyncSession):
            #ge greater or equal (>=1)

        logger.info(f"Getting posts (page={page}, page_size={page_size})")

        cache_key = f"cache:posts:page:{page}:page_size:{page_size}:sort_by:{sort_by}"

        cached_posts = await cache_get(cache_key)
        if cached_posts:
            logger.info(f"Found cached posts (page={page}, page_size={page_size})")
            return json.loads(cached_posts)

        total = await post_repository.count_all(db)

        offset = (page - 1) * page_size

        if sort_by == PostSortBy.newest:
            order_clause = desc(Post.created_at)
        elif sort_by == PostSortBy.oldest:
            order_clause = Post.created_at
        else:
            order_clause = desc(text("likes_count"))

        rows = await post_repository.get_all(db, order_clause, page_size, offset)

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


    async def get_post(self, post_id: int, db: AsyncSession):

        logger.info(f"Getting post with id {post_id}")

        cache_key = f"cache:posts:post:{post_id}"
        cached = await cache_get(cache_key)

        if cached:
            logger.info(f"Found cached post with id {post_id}")
            return PostResponse(**json.loads(cached))

        row = await post_repository.get_by_id(db, post_id)

        if not row:
            logger.warning(f"Post with id {post_id} not found")
            return None

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


    async def delete_post(self, post_id: int, current_user: User, db: AsyncSession):

        logger.info(f"Deleting post with id {post_id}")

        post = await post_repository.get_simple(db, post_id)

        if not post:
            logger.warning(f"Post with id {post_id} not found")
            return "Post not found"

        if post.user_id != current_user.id:
            logger.warning(f"User {current_user.id} tried to delete post {post_id} of user {post.user_id}")
            return "forbidden"

        await post_repository.delete(db, post)

        logger.info(f"Deleted post with id {post_id}")

        await cache_pattern_delete("cache:posts:*")
        logger.info(f"Cache pattern deleted")

        return


    async def update_post(self, post_id: int, post_data: PostUpdate, current_user: User,db: AsyncSession):

        logger.info(f"Getting post with id {post_id}")

        post = await db.get(Post, post_id)

        if not post:
            logger.warning(f"Post with id {post_id} not found")
            return None

        if post.user_id != current_user.id:
            logger.warning("User not allowed to update post")
            return "forbidden"

        updates = post_data.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(status_code=404, detail="No fields to update")

        for key, value in updates.items():
            setattr(post, key, value)

        post.updated_at = datetime.now()

        await post_repository.update(db, post)

        await cache_pattern_delete("cache:posts:*")
        logger.info(f"Cache pattern cleared in Redis")


        return PostResponse.model_validate(post)


    async def get_feed(self, page: int, page_size: int, current_user: User, db: AsyncSession):

        logger.info(f"Getting feed for user {current_user.id}")

        cache_key = f"cache:feed:{current_user.id}:page{page}"
        cached = await cache_get(cache_key)
        if cached:
            return json.loads(cached)

        offset = (page - 1) * page_size

        rows = await post_repository.get_feed(db, current_user, page_size, offset)
        total = await post_repository.get_feed_count(db, current_user)

        posts_data = []

        for post, likes_count, comment_count, score in rows:
            posts_data.append({
                "id": post.id,
                "body": post.body,
                "user_id": post.user_id,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
                "likes_count": likes_count or 0
            })

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

