from fastapi import APIRouter

from myapp.base.response import CommonResponse


class MyRouter(APIRouter):
    """
    重写fastAPIP的APIRouter。设置route_class为CustomResponseRoute和自动为每个API添加422 response校验
    """

    def __init__(self, *args, **keywords):
        if not keywords.get("responses"):
            keywords["responses"] = {}
        keywords["responses"].update(CommonResponse.RequestValidationErrorResponse)
        keywords["responses"].update(CommonResponse.NotFoundErrorResponse)
        keywords["responses"].update(CommonResponse.DefaultErrorResponse)
        super(MyRouter, self).__init__(*args, **keywords)
