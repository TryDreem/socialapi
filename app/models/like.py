from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from app.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class Like(Base):
    """
      -id
      -post_id
      -user_id
      -created_at

    """
    __tablename__ = "likes"


    __table_args__ = (
        UniqueConstraint("user_id", "post_id",  name="unique_user_post_like"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    #for comment.post one comment had one comment
    post: Mapped["Post"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship(back_populates="likes")

    def __repr__(self) -> str:
        return f"<Post {self.post_id} has been liked by {self.user_id}>)>"