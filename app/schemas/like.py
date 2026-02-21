from pydantic import BaseModel, ConfigDict
from datetime import datetime



class LikeResponse(BaseModel):
    id: int
    user_id: int
    post_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LikeCountResponse(BaseModel):
    post_id: int
    count: int
