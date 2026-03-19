from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, ValidationError
from datetime import datetime
from typing import List


class PostCreate(BaseModel):
    body : str

    @field_validator("body")
    @classmethod
    def validate_body(cls, v):
        if not v or not v.strip():
            raise ValueError("Post body cannot be empty")
        if len(v) > 500:
            raise ValueError("Post body cannot be longer than 500 characters")
        return v.strip()

class PostUpdate(BaseModel):
    body : str | None = None


class PostResponse(BaseModel):
    id: int
    body: str
    user_id: int
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class PostsResponse(BaseModel):
    posts: List[PostResponse]

