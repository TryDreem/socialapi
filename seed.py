import asyncio
from app.database import AsyncSessionLocal
from app.models import User, Post, Like, Comment, Follow
from app.core.security import get_password_hash


async def seed():
    async with AsyncSessionLocal() as db:
        user1 = User(email="elonmask@gmail.com", password_hash=get_password_hash("12345678"), is_confirmed=True)
        user2 = User(email="trump@gmail.com", password_hash=get_password_hash("12345678"), is_confirmed=True)
        user3 = User(email="vlad@gmail.com", password_hash=get_password_hash("12345678"), is_confirmed=True)
        user4 = User(email="ronaldo@gmail.com", password_hash=get_password_hash("12345678"), is_confirmed=True)
        user5 = User(email="messi@gmail.com", password_hash=get_password_hash("12345678"), is_confirmed=True)
        db.add_all([user1, user2, user3, user4, user5])
        await db.commit()

        post1 = Post(body="SpaceX top", user_id=user1.id)
        post2 = Post(body="X.com", user_id=user1.id)
        post3 = Post(body="Buy Trump coin here", user_id=user2.id)

        db.add_all([post1, post2, post3])
        await db.commit()

        comment1 = Comment(body="NASA better", user_id=user4.id, post_id=post1.id)
        comment2 = Comment(body="I dont think so", user_id=user5.id, post_id=post1.id)
        comment3 = Comment(body="BTC better", user_id=user3.id, post_id=post3.id)

        db.add_all([comment1, comment2, comment3])
        await db.commit()

        like1 = Like(post_id=post1.id, user_id=user2.id)
        like2 = Like(post_id=post1.id, user_id=user3.id)
        like3 = Like(post_id=post1.id, user_id=user4.id)
        like4 = Like(post_id=post2.id, user_id=user3.id)
        like5 = Like(post_id=post3.id, user_id=user1.id)
        like6 = Like(post_id=post3.id, user_id=user5.id)

        db.add_all([like1, like2, like3, like4, like5, like6])
        await db.commit()

        follow1 = Follow(follower_id=user2.id, following_id=user1.id)
        follow2 = Follow(follower_id=user3.id, following_id=user1.id)
        follow3 = Follow(follower_id=user4.id, following_id=user1.id)
        follow4 = Follow(follower_id=user1.id, following_id=user2.id)
        follow5 = Follow(follower_id=user5.id, following_id=user2.id)

        db.add_all([follow1, follow2, follow3, follow4, follow5])
        await db.commit()

        print("Seed completed successfully")

if __name__ == "__main__":
    asyncio.run(seed())



