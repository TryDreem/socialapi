from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.database import get_db
from sqlalchemy import select
from app.schemas.user import UserRegister, UserResponse
from app.models.user import User


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserRegister, db: AsyncSession = Depends(get_db)):

    statement = select(User).where(User.email == user.email)
    result = await db.execute(statement)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)


    db_user = User(
        email=user.email,
        password_hash=hashed_password,
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserResponse.model_validate(db_user)




