from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException
from app.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(email: str) -> str:

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": email,
        "exp": expire,
        "type": "access"
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        expire = payload.get("exp")
        if expire < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Expired token")

        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(status_code=403, detail="Invalid token")

        email = payload.get("sub")

        return email

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

