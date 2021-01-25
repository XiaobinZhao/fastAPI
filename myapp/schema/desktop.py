from typing import Optional
from uuid import uuid4
from pydantic import BaseModel, Field
from myapp.base.schema import SchemaMetaclass
from myapp.base.schema import EnabledEnum
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
    uuid: str = Field(default=uuid4().hex, description="业务中使用的桌面uuid")
    node_name: str = Field(max_length=255)
    vm_uuid: str = Field(max_length=64)
    node_uuid: str = Field(max_length=64)
    enabled: EnabledEnum = Field(EnabledEnum.enabled)
    is_attached_gpu: bool = Field(False)
