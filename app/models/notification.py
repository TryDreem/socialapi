from datetime import datetime
from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.post import Post
    from app.models.user import User

class NotificationType(str, enum.Enum):
    like = "like"
    comment = "comment"
    follow = "follow"



class Notification(Base):
    """
    -id
    -user_id
    -actor_id
    -type
    -post_id
    -is_read
    -created_at
    """
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    actor_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    type: Mapped[NotificationType] = mapped_column()
    post_id: Mapped[Optional[int]]  = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(foreign_keys=[user_id], back_populates="notifications")
    post: Mapped[Optional["Post"]] = relationship(back_populates="notifications")


    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, user_id={self.user_id})>"

