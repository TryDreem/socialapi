from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from sqlalchemy import select, desc

from app.schemas.post import PostResponse, PostCreate, PostsResponse, DeleteResponse
from app.models.user import User
from app.models.post import Post
from app.api.deps import get_current_user



import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/post", tags=["post"])


@router.post("", response_model=PostResponse, status_code=201)
async def create_post(
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

    return PostResponse.model_validate(db_post)

@router.get("", response_model=PostsResponse, status_code=200)
async def get_all_posts(
        limit: int = 20,
        db: AsyncSession = Depends(get_db)
):
    logger.info(f"Getting all posts")

    query = select(Post).order_by(desc(Post.created_at)).limit(limit)
    result = await db.execute(query)
    posts = result.scalars().all()

    return PostsResponse(posts=posts)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
        post_id: int,
        db: AsyncSession = Depends(get_db),
):
    logger.info(f"Getting post with id {post_id}")

    post = await db.get(Post, post_id)

    if not post:
        logger.warning(f"Post with id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")


    return PostResponse.model_validate(post)


@router.delete("/{post_id}",response_model=DeleteResponse, status_code=200)
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

    return DeleteResponse.model_validate({"message": f"Post (id: {post_id}) deleted successfully"})

