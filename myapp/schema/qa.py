from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from pydantic import root_validator
from myapp.base.schema import SchemaMetaclass
from myapp.base.schema import EnabledEnum
from myapp.base.schema import optional_but_cant_empty
from myapp.models.qa import Qa


class QaBase(BaseModel, metaclass=SchemaMetaclass):
    title: str = Field("", max_length=255)
    is_default: bool = Field(False)
    desc: Optional[str] = Field("", max_length=255)

    class Config:
        orm_mode = True
        orm_model = Qa

class QaDetail(QaBase):
    """
    QA详情对象
    """
    uuid: str = Field("", max_length=64)
    # download_url: str = Field("", max_length=255)
    # group: str = Field("", max_length=255)
    # last: str = Field(max_length=255)
    # next: str = Field(max_length=64)
    # asklist: str = Field(max_length=64)
    created_at: Optional[datetime] = Field()
    updated_at: Optional[datetime] = Field()


class QaPatch(QaBase):
    enabled: Optional[EnabledEnum] = Field()
    title: Optional[str] = Field(max_length=255)
    is_default: Optional[bool] = Field()
    desc: Optional[str] = Field(max_length=255)

    _root_validator = root_validator(pre=True, allow_reuse=True)(optional_but_cant_empty)