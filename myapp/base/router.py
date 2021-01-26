import json
from typing import Callable
from fastapi import Response
from fastapi import Request
from fastapi import APIRouter
from fastapi.routing import APIRoute
from myapp.base.response import CommonResponse
from myapp.base.schema import MyBaseSchema


class CustomResponseRoute(APIRoute):
    """
    自定义router handler。修改response body，包装response body为MyBaseSchema数据结构
    """
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            response_body = json.loads(response.body.decode())
            custome_response = MyBaseSchema(data=response_body)
            response.body = json.dumps(custome_response.dict()).encode()
            for index, value in enumerate(response.headers.raw):
                if b'content-length' in value:
                    response.headers.raw[index] = (b'content-length', str(len(response.body)).encode())

            return response

        return custom_route_handler


class MyRouter(APIRouter):
    """
    重写fastAPIP的APIRouter。设置route_class为CustomResponseRoute和自动为每个API添加422 response校验
    """
    def __init__(self, *args, **keywords):
        if not keywords.get("responses"):
            keywords["responses"] = {}
        keywords["responses"].update(CommonResponse.RequestValidationErrorResponse)
        keywords["responses"].update(CommonResponse.DefaultErrorResponse)
        keywords["route_class"] = CustomResponseRoute
        super(MyRouter, self).__init__(*args, **keywords)
