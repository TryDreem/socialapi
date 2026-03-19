from pydantic import BaseModel, ConfigDict

class FollowResponse(BaseModel):
    # A follows B
    follower_id: int  # A
    following_id: int # B

    model_config = ConfigDict(from_attributes=True)


class UserShortResponse(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)


class FollowersResponse(BaseModel):
    followers: list[UserShortResponse]
