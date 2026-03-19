from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.database import Base
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.models.user import User


class Follow(Base):
    """
     -follower_id
     -following_id
    """
    __tablename__ = "follows"

    follower_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    following_id : Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    follower: Mapped["User"] = relationship(foreign_keys=[follower_id],back_populates="following")
    following: Mapped["User"] = relationship(foreign_keys=[following_id],back_populates="followers")

    def __repr__(self) -> str:
        return f"{self.follower_id} follows {self.following_id})"