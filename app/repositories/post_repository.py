from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.post import Post
from app.models.like import Like
from app.models.follow import Follow
from app.models.comment import Comment
from app.models.user import User


class PostRepository:
    async def get_simple(self, db: AsyncSession, post_id: int):
        query = select(Post).where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()

        return post


    async def get_by_id(self, db: AsyncSession, post_id: int):
        query = (select(Post, func.count(Like.id).label("like_count"))
                 .outerjoin(Like, Post.id == Like.post_id)
                 .where(Post.id == post_id)
                 .group_by(Post.id)
        )
        result = await db.execute(query)

        return result.first()


    async def count_all(self, db: AsyncSession):
        count_query = select(func.count(Post.id))
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        return total

    async def get_all(self, db:AsyncSession, order_clause: Any, page_size: int, offset: int):
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
        return rows

    async def get_feed(self, db:AsyncSession, current_user: User, page_size, offset):
        base_posts = (
            select(Post.id, Post.created_at)
            .join(Follow, Post.user_id == Follow.following_id)
            .where(Follow.follower_id == current_user.id)
            .subquery()
        )

        likes_subq = (
            select(
                Like.post_id,
                func.count().label("likes_count")
            )
            .where(Like.post_id.in_(select(base_posts.c.id)))
            .group_by(Like.post_id)
            .subquery()
        )

        comments_subq = (
            select(
                Comment.post_id,
                func.count().label("comments_count")
            )
            .where(Comment.post_id.in_(select(base_posts.c.id)))
            .group_by(Comment.post_id)
            .subquery()
        )

        score = (
                func.coalesce(likes_subq.c.likes_count, 0) * 3 +
                func.coalesce(comments_subq.c.comments_count, 0) * 5 -
                func.extract('epoch', func.now() - Post.created_at) / 3600 * 0.1
        ).label("score")


        query = (
            select(
                Post,
                func.coalesce(likes_subq.c.likes_count, 0).label("likes_count"),
                func.coalesce(comments_subq.c.comments_count, 0).label("comments_count"),
                score,
            )
            .join(base_posts, Post.id == base_posts.c.post_id)
            .outerjoin(likes_subq, Post.id == likes_subq.c.post_id)
            .outerjoin(comments_subq, Post.id == comments_subq.c.post_id)
            .order_by(score.desc())
            .limit(page_size)
            .offset(offset)
        )

        result = await db.execute(query)
        rows = result.all()
        return rows


    async def get_feed_count(self, db: AsyncSession, current_user: User):
        count_query = (
            select(func.count(Post.id))
            .join(Follow, Post.user_id == Follow.following_id)
            .where(Follow.follower_id == current_user.id)
        )

        total = (await db.execute(count_query)).scalar()

        return total


    async def count_search(self, db:AsyncSession, q: str):
        count_query = (
            select(func.count(Post.id))
            .where(Post.body.like(f"%{q}%"))
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        return total


    async def search(self, db: AsyncSession, order_clause: Any, page_size: int, offset: int, q: str):
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
        return rows

    async def create(self, db:AsyncSession, post: Post):
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post


    async def delete(self, db:AsyncSession, post: Post):
        await db.delete(post)
        await db.commit()


    async def update(self, db: AsyncSession, post: Post):
        await db.commit()
        await db.refresh(post)
        return post


post_repository = PostRepository()