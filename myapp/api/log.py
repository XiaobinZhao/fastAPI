import json
from typing import List

from fastapi import Depends, Query
from fastapi.requests import Request

from myapp.base.router import MyRouter
from myapp.base.schema import MyBaseSchema, PageSchema, MyFilterQueryParam
from myapp.error_code.user import SuccessCode
from myapp.base.tools import aes_decrypt
from myapp.conf.config import settings
from myapp.error_code.log import SuccessCode
from myapp.exception.auth import RequestSecretInvalidException
from myapp.manager.log import LogManager
from myapp.manager.token import verify_token
from myapp.schema.token import SecretRequestSchema
from myapp.schema.log import LogBase as LogBaseSchema
from myapp.schema.log import LogCreateRequest as LogCreateRequestSchema

router = MyRouter(prefix="/logs", tags=["log"])


@router.get("/", response_model=MyBaseSchema[PageSchema[List[LogBaseSchema]]],
            dependencies=[Depends(verify_token)])
async def list_logs(search_key: str = "operation_desc", search_str: str = "",
                    filters: MyFilterQueryParam = Query(default={}, description="其他过滤条件，必须符合a=xx,b=xx的键值对格式"),
                    skip: int = 0, limit: int = 100):
    """
    查询用户列表.
    """
    manager = LogManager()
    users = await manager.list_logs(search_key=search_key, search_str=search_str, filters=filters,
                                    skip=skip, limit=limit)
    return MyBaseSchema[PageSchema[List[LogBaseSchema]]](data=users, code=SuccessCode.SUCCESS()["code"])


@router.post("/", response_model=MyBaseSchema[LogBaseSchema])
async def create_log(reqeust_secret: SecretRequestSchema, request: Request):
    plan_text = aes_decrypt(reqeust_secret.secret, settings.identity.aes_secret_key)
    try:
        plan_text = json.loads(plan_text)
    except json.JSONDecodeError as e:
        raise RequestSecretInvalidException(message=f"日志创建的加密请求数据结构异常：{plan_text}")
    try:
        params = LogCreateRequestSchema.validate(plan_text)
    except Exception as e:
        raise RequestSecretInvalidException(message=f"日志创建的请求明文数据结构异常：{plan_text}, {str(e)}")

    manager = LogManager()
    feedback = await manager.create_log(params, request)
    return MyBaseSchema[LogBaseSchema](data=feedback, code=SuccessCode.SUCCESS()["code"])

