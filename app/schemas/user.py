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


class UserLogin(BaseModel):
    email: EmailStr
    password: str