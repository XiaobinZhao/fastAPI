from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from myapp.base.schema import SchemaMetaclass
from myapp.models.desktop import Desktop
from myapp.schema.common import EnabledEnum


class DesktopBase(BaseModel, metaclass=SchemaMetaclass):
    display_name: str = Field(max_length=255)
    is_default: bool = Field(False)
    desc: Optional[str] = Field("", max_length=255)

    class Config:
        orm_mode = True
        orm_model = Desktop


class DesktopDetail(DesktopBase):
    uuid: UUID = Field(default_factory=uuid4, description="业务中使用的桌面uuid")
    node_name: str = Field(max_length=255)
    vm_uuid: str = Field(max_length=64)
    node_uuid: str = Field(max_length=64)
    enabled: EnabledEnum = Field(EnabledEnum.enabled)
    is_attached_gpu: bool = Field(False)


