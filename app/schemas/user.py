from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, ValidationError
from datetime import datetime



class UserRegister(BaseModel):

    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class UserResponse(BaseModel):
    id : int
    email: str
    is_confirmed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"



class RefreshToken(BaseModel):
    refresh_token: str