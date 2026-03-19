from datetime import datetime
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.comment import Comment
    from app.models.like import Like
    from app.models.follow import Follow


class User(Base):
    """
    -id
    -email
    -password
    -is_confirmed
    -created_at

    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    is_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    comments: Mapped[list["Comment"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    likes: Mapped[list["Like"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    followers: Mapped[list["Follow"]] = relationship(foreign_keys="Follow.following_id", back_populates="follower")

    following: Mapped[list["Follow"]] = relationship(foreign_keys="Follow.follower_id",back_populates="following")


    def __repr__(self):
            return f"<User(id={self.id}, email={self.email})>"

