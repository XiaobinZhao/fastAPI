from datetime import datetime
from typing import Optional

from myapp.base.schema import MyTimestamp
from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(description="jwt token")
    token_type: str = Field(default="bearer", description="token type")
    user_uuid: str = Field(description="user uuid")
    created_at: MyTimestamp = Field(default=datetime.now(), description="创建时间点")
    expired_at: MyTimestamp = Field(description="过期时间点")


class TokenPayload(BaseModel):
    uuid: str = Field(max_length=64, description="token uuid")
    login_name: str = Field(max_length=64, description="用户登录名")
    user_uuid: str = Field(max_length=64, description="用户uuid")


class SecretRequestSchema(BaseModel):
    """
    不使用token进行API调用时需要把参数进行加密传输。其中secret是经过aes加密的字符串，明文结构类似于这样的json
    {“user_name”: “xx@xx.com”, "password": "xxxx", "token": "xxxx"}
    """
    secret: str = Field(description="json结构的加密信息")
    timestamp: Optional[int] = Field(description="时间戳")
