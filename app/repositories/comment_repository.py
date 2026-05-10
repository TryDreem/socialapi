from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.comment import Comment
from app.models.post import Post


class CommentRepository:
    async def create(self, db:AsyncSession, comment: Comment):
        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment

    async def get_total_count(self, db: AsyncSession, post_id: int):
        count_query = select(func.count(Comment.id)).where(Comment.post_id==post_id)
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        return total


    async def get_all(self, db: AsyncSession, post_id: int, page_size: int, offset: int):
        query = (select(Comment)
                 .where(Comment.post_id==post_id)
                 .order_by(Comment.created_at)
                 .limit(page_size)
                 .offset(offset)
                 )

        result = await db.execute(query)
        comments = result.scalars().all()

        return comments

    async def delete(self,db: AsyncSession, comment: int):
        await db.delete(comment)
        await db.commit()


comment_repository = CommentRepository()