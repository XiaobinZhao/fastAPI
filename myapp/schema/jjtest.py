from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import root_validator
from myapp.base.schema import SchemaMetaclass
from myapp.base.schema import EnabledEnum
from myapp.base.schema import optional_but_cant_empty
from myapp.models.jjtest import Jjtest

class JjtestBase(BaseModel, metaclass=SchemaMetaclass):
    display_name: str = Field(max_length=255)
    login_name: str = Field(max_length=64)
    email: str = Field(default="", max_length=255)
    enabled: EnabledEnum = Field(EnabledEnum.enabled)
    desc: Optional[str] = Field(default="", max_length=255)
    age: Optional[int] = Field()
    sex: bool = Field()
    time: Optional[datetime] = Field()
    
    class Config:
        orm_mode = True
        orm_model = Jjtest

class JjtestDetail(JjtestBase):
    uuid: str = Field(max_length=64)
    created_at: Optional[datetime] = Field()
    updated_at: Optional[datetime] = Field()
    
class JjtesCreate(JjtestBase):
    password: str = Field(max_length=255)
    
class JjtestPatched(JjtestBase):
    display_name: Optional[str] = Field(max_length=255)
    login_name: Optional[str] = Field(max_length=64)
    email: Optional[str] = Field(max_length=255)
    enabled: Optional[EnabledEnum] = Field()
    desc: Optional[str] = Field(max_length=255)
    age: Optional[int] = Field()
    sex: Optional[bool] = Field()
    time: Optional[datetime] = Field()

    _root_validator = root_validator(pre=True, allow_reuse=True)(optional_but_cant_empty)