from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, ValidationError
from datetime import datetime
from typing import List




class CommentCreate(BaseModel):
    body: str



class CommentResponse(BaseModel):
    id: int
    body: str
    post_id: int
    user_id: int
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)



class CommentsResponse(BaseModel):
    comments: List[CommentResponse]

    model_config = ConfigDict(from_attributes=True)
