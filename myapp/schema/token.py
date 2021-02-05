from datetime import datetime
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(description="jwt token")
    token_type: str = Field(default="bearer", description="token type")
    user_uuid: str = Field(description="user uuid")
    created_at: datetime = Field(default=datetime.now(), description="创建时间点")
    expired_at: datetime = Field(description="过期时间点")


class TokenPayload(BaseModel):
    login_name: str = Field(max_length=64, description="jwt所面向用户的用户登录名")
    user_uuid: str = Field(max_length=64, description="jwt所面向用户的用户uuid")

