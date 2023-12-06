import json

import shortuuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import Message

from myapp.base.context import request_id_var, request_cycle_context

REQUEST_ID_HEADER_KEY = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    在request中新增X-Request-ID header，方便日志追踪;以及其他request信息
    """

    async def set_body(self, request):
        """
        必须新增这个方法，否则不能访问request.body()
        但是看起来可能不那么美观，可以使用fastapi dependency代替
        ref https://github.com/encode/starlette/issues/495
        """
        receive_ = await request.receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive

    async def dispatch(self, request: Request, call_next):
        # request请求时长暂时用不到，先注释掉
        # import time
        # start_time = time.time()
        # request_context.update({"start_at": start_time})

        # 默认值类似于`req-BioLA5VxyV8dih4BCZWmf5`
        req_id = f"req-{shortuuid.uuid()}"
        request_id_var.set(request.headers.get(REQUEST_ID_HEADER_KEY, req_id))

        await self.set_body(request)
        request_info = {
            "req_id": req_id,
            "request_ip": request.client.host,
            "request_params": json.dumps({
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers.items()),
                "params": str(request.query_params),
                "body": (await request.body()).decode()
            }).encode()
        }

        with request_cycle_context(request_info):
            response = await call_next(request)

            # request请求时长暂时用不到，先注释掉
            # end_time = time.time()
            # process_time = (end_time - start_time) * 1000
            # formatted_process_time = "{0:.2f}".format(process_time)
            #
            # request_context.update({"request_end_at": end_time, "request_elapsed_time": f"{formatted_process_time}ms"})
            # response.headers["request_elapsed_time"] = f"{formatted_process_time}ms"

            request_id = request_id_var.get()
            if request_id:
                response.headers[REQUEST_ID_HEADER_KEY] = request_id
            return response


async def add_request_info_to_request_context(request: Request):
    """
    使用fastapi的dependency设置request信息到contextvar
    本方法的dependency和RequestContextMiddleware 不能同时使用。
    否则需要修改request_cycle_context中context初始化的方法
    """
    import json
    request_info = {
        "request_ip": request.client.host,
        "request_params": json.dumps({
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers.items()),
            "params": str(request.query_params),
            "body": (await request.body()).decode()
        }).encode()
    }

    with request_cycle_context(request_info):
        # yield allows it to pass along to the rest of the request
        # ref https://github.com/tomwojcik/starlette-context/blob/v0.3.6/docs/source/fastapi.rst
        yield
