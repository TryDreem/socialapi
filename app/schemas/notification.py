from typing import Optional

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    actor_id: int
    type: str
    post_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)