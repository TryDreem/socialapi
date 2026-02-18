from datetime import datetime
from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import  Mapped, mapped_column
from app.database import Base



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

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

