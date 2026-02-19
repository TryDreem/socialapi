from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, create_confirmation_token, decode_confirmation_token
from app.database import get_db
from sqlalchemy import select
from app.schemas.user import UserRegister, UserResponse, UserLogin, Token
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user
from app.services.email import send_confirmation_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserRegister, background_tasks: BackgroundTasks,db: AsyncSession = Depends(get_db)):

    query = select(User).where(User.email == user.email)
    result = await db.execute(query)
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

    confirmation_token = create_confirmation_token(user.email)

    confirmation_url = f"http://localhost:8000/auth/confirm?token={confirmation_token}"

    background_tasks.add_task(send_confirmation_email,
                              user.email,
                              confirmation_url)


    return UserResponse.model_validate(db_user)



@router.post("/login", response_model=Token, status_code=200)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == credentials.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_confirmed:
        raise HTTPException(status_code=400, detail="Email not confirmed")

    token = create_access_token(user.email)

    return Token(access_token=token)



@router.get("/confirm")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    email = decode_confirmation_token(token)
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    if user.is_confirmed:
        raise HTTPException(status_code=400, detail="Email already confirmed")

    user.is_confirmed = True
    await db.commit()

    return {"message": "Email confirmed successfully! You can now login."}




@router.get("/me", response_model=UserResponse, status_code=200)
async def get_current_user_info(
        current_user: User = Depends(get_current_user)
):
    return UserResponse.model_validate(current_user)





