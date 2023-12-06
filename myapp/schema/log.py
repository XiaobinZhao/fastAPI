from typing import Optional, TypeVar

from pydantic import BaseModel, Field

from myapp.base.constant import UserTypeEnum, LogStatusEnum, LogResourceAppTypeEnum
from myapp.base.schema import SchemaMetaclass, MyTimestamp
from myapp.models.log import Log


ResponseData = TypeVar("ResponseData")


class LogBase(BaseModel, metaclass=SchemaMetaclass):
    uuid: str = Field(default="", max_length=64)
    user_uuid: str = Field(default="", max_length=64)
    user_email: str = Field(default="")
    user_type: UserTypeEnum = Field(default="")
    app_type: LogResourceAppTypeEnum = Field(default="")
    app_release: str = Field(default="")
    level: str = Field(default="")
    domain: str = Field(default="")
    sub_domain: str = Field(default="")
    action: str = Field(default="", max_length=255)
    obj_id: str = Field(default="", max_length=64)
    obj_name: str = Field(default="", max_length=255)
    ref_id: str = Field(default="", max_length=255)
    ref_name: str = Field(default="", max_length=255)
    req_id: str = Field(default="")
    status: LogStatusEnum = Field(default="")
    request_ip: str = Field(default="", max_length=20)
    error_code: str = Field(default="", max_length=64)
    error_message: str = Field(default="")
    operation_desc: str = Field(default="")
    extra: str = Field(default="")
    request_params: str = Field(default="")
    response_body: str = Field(default="")
    created_at: Optional[MyTimestamp] = Field()
    updated_at: Optional[MyTimestamp] = Field()

    class Config:
        orm_mode = True
        orm_model = Log


class LogCreateRequest(BaseModel, metaclass=SchemaMetaclass):
    user_email: str = Field(default="", description="如果有user登录，那么存放用户邮箱，否则是空字符串")
    app_type: LogResourceAppTypeEnum = Field(default=LogResourceAppTypeEnum.web,
                                             description="表示发送的app类型，可以是 android, ios, web")
    app_release: str = Field(default="")
    level: str = Field(default="1", description="日志级别,DEBUG: 1, INFO: 2, ALERT: 3, ERROR: 4, FATAL: 5")
    domain: str = Field(default="", description="表示这个log是关于哪个方面问题")
    sub_domain: str = Field(default="", description="表示这个log是哪个细节方面的问题")
    content: str = Field(default="")
