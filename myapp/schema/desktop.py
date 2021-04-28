from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import root_validator
from myapp.base.schema import SchemaMetaclass
from myapp.base.schema import EnabledEnum
from myapp.base.schema import optional_but_cant_empty
from myapp.models.desktop import Desktop


class DesktopBase(BaseModel, metaclass=SchemaMetaclass):
    display_name: str = Field(max_length=255)
    is_default: bool = Field(False)
    desc: Optional[str] = Field("", max_length=255)

    class Config:
        orm_mode = True
        orm_model = Desktop


class DesktopDetail(DesktopBase):
    """
    桌面详情对象
    """
    uuid: str = Field(max_length=64, description="业务中使用的桌面uuid")
    node_name: str = Field(max_length=255)
    vm_uuid: str = Field(max_length=64)
    node_uuid: str = Field(max_length=64)
    enabled: EnabledEnum = Field(EnabledEnum.enabled)
    is_attached_gpu: bool = Field(False)
    created_at: Optional[datetime] = Field()
    updated_at: Optional[datetime] = Field()


class DesktopPatch(DesktopBase):
    enabled: Optional[EnabledEnum] = Field()
    is_attached_gpu: Optional[bool] = Field()
    display_name: Optional[str] = Field(max_length=255)
    is_default: Optional[bool] = Field()
    desc: Optional[str] = Field(max_length=255)

    _root_validator = root_validator(pre=True, allow_reuse=True)(optional_but_cant_empty)