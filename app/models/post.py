from datetime import datetime
from typing import Optional, TYPE_CHECKING

from annotated_types.test_cases import cases
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.comment import Comment
    from app.models.like import Like




class Post(Base):
    """
    -id
    -body
    -user_id
    =author
    -created_at
    -updated_at

    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    body: Mapped[str] = mapped_column(String(500))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(default=None, onupdate=datetime.utcnow)

    author: Mapped["User"] = relationship(back_populates="posts")

    #one post has many comments and if delete post all comments will disappear
    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")

    likes: Mapped[list["Like"]] = relationship(back_populates="post", cascade="all, delete-orphan")


    def __repr__(self) -> str:
            return f"<Post(id={self.id}, author_id={self.user_id})>"


