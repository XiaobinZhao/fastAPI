import json
from datetime import datetime
from functools import wraps
from uuid import uuid4

from loguru import logger
from fastapi.requests import Request

from myapp.base.constant import LogStatusEnum
from myapp.base.schema import PageSchema, MyBaseSchema
from myapp.models.log import Log as DB_Log_Model
from myapp.schema.log import LogCreateRequest as LogCreateRequestSchema


class LogManager(object):
    def __init__(self, *args, **keywords):
        super(LogManager, self).__init__(*args, **keywords)

    @staticmethod
    async def list_logs(search_key: str = "", search_str: str = "", filters=None, skip: int = 0, limit: int = 100):
        logs, total_count = await DB_Log_Model.async_filter(is_get_total_count=True, search_key=search_key,
                                                            search_str=search_str, offset=skip,
                                                            limit=limit, **filters)
        return PageSchema(total=total_count, limit=limit, skip=skip, data=logs)

    async def create_log(self, create_request: LogCreateRequestSchema, request: Request):
        create_request_dict = create_request.dict()
        create_request_dict["request_params"] = create_request.content.encode()  # app请求的content保存在request params
        create_request_dict["status"] = LogStatusEnum.success.value
        create_request_dict["request_ip"] = request.client.host or "127.0.0.1"

        return await self.record_log(**create_request_dict)

    @classmethod
    async def record_log(cls, **kwargs):
        _request = kwargs.pop('request', None)
        if _request:
            kwargs['request_params'] = await cls.json_transform(_request)
            kwargs["request_ip"] = _request.client.host or "127.0.0.1"
        else:
            kwargs["request_ip"] = "127.0.0.1"
        new_log = DB_Log_Model(**kwargs)
        new_log.uuid = uuid4().hex
        return await new_log.async_create()

    @staticmethod
    async def json_transform(_request):
        return json.dumps({
            "method": _request.method,
            "url": str(_request.url),
            "headers": dict(_request.headers.items()),
            "params": str(_request.query_params),
            "body": (await _request.body()).decode()
        }).encode()


class LogWrapper(object):
    """
    操作日志装饰器，使用async with语法
    """

    def __init__(self, domain, action, status=LogStatusEnum.unknown, request_ip=""):

        self.log_db_model = DB_Log_Model(uuid=uuid4().hex, action=action, domain=domain, status=status,
                                         request_ip=request_ip)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_traceback):
        self.log_db_model.updated_at = datetime.now()
        if exc_type:
            error_message = getattr(exc_val, "message", "") or str(exc_val) or exc_traceback.tb_frame
            self.log_db_model.status = "fail"
            self.log_db_model.error_message = error_message
            self.log_db_model.error_code = exc_val.code if hasattr(exc_val, "code") else ""
        else:
            if self.log_db_model.status == "unknown":
                self.log_db_model.status = "success"
        await self.log_db_model.async_create()


def log(domain, action, **out_kwargs):
    """
    记录操作日志的装饰器.
    :param out_kwargs: 其他参数
    :param domain: 日志分类，比如order的部分.
    :param action: 动作定义.如创建
    """

    def decorator(func):
        @wraps(func)  # 保留func的重要的元信息比如名字、文档字符串、注解和参数签名
        async def wrapper(*args, **kwargs):
            async with LogWrapper(domain=domain, action=action) as log_context:
                log_context.log_db_model.operation_desc = f"{action} {domain}"

                for k, v in out_kwargs.items():
                    setattr(log_context.log_db_model, k, v)

                async def set_log_request_params(_request):
                    log_context.log_db_model.request_ip = log_context.log_db_model.request_ip \
                                                          or _request.client.host or "127.0.0.1"
                    log_context.log_db_model.request_params = await LogManager.json_transform(_request)

                def set_request_extra_params():
                    log_params = kwargs.get("log_params", {})
                    for _k, _v in log_params.items():
                        if _k == "response_body":
                            log_context.log_db_model.response_body = str(_v).encode()
                        elif _k == "request_params":
                            log_context.log_db_model.request_params = json.dumps(_v).encode()
                        else:
                            setattr(log_context.log_db_model, _k, _v)

                request_before_func = kwargs.get("request", None)
                if request_before_func:
                    await set_log_request_params(request_before_func)
                set_request_extra_params()

                func_return = None
                try:
                    func_return = await func(*args, **kwargs)
                except Exception as e:
                    raise e  # 有异常正常抛出
                finally:  # 但是一定要把log的上下文处理完成
                    # 可能在func 执行完成之后才会设置REQUEST对象
                    request_after_func = kwargs.get("request", None)
                    if request_after_func:
                        if getattr(request_after_func, "obj_id", ""):
                            log_context.log_db_model.obj_id = request_after_func.obj_id
                        if not request_before_func:  # 如果是在func之前设置的request，不用再次处理
                            await set_log_request_params(request_after_func)
                        # 处理操作用户信息
                        token_payload = getattr(request_after_func, "token_payload", None)
                        if token_payload:
                            log_context.log_db_model.user_type = token_payload[0]
                            log_context.log_db_model.user_uuid = token_payload[1]["user_uuid"]
                            log_context.log_db_model.user_email = token_payload[1]["user_email"]
                        else:  # 如果没有payload，一般是登录操作，直接从request获取
                            log_context.log_db_model.user_uuid = getattr(request_after_func, "user_uuid", "")
                            log_context.log_db_model.user_email = getattr(request_after_func, "user_email", "")

                        # 如果API自己设置了描述，则优先取API设置的
                        log_context.log_db_model.operation_desc = getattr(request_after_func, "operation_desc",
                                                                          "") or log_context.log_db_model.operation_desc

                    if isinstance(func_return, MyBaseSchema):
                        log_context.log_db_model.response_body = str(func_return.json()).encode()

                    # 设置其他的隐含参数
                    set_request_extra_params()

                    logger.info(log_context.log_db_model.to_dict())

                return func_return

        return wrapper

    return decorator
