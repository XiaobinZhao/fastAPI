from fastapi import status
from fastapi.responses import JSONResponse
from myapp.base.schema import MyBaseSchema


class CommonResponse:
    DefaultErrorResponse = {status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": MyBaseSchema}}
    NotFoundErrorResponse = {status.HTTP_404_NOT_FOUND: {"model": MyBaseSchema}}
    RequestValidationErrorResponse = {status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": MyBaseSchema}}


class MyBaseResponse(JSONResponse):
    """
    统一response的返回值结构
    """
    def __init__(self, code, message="", data={}, status_code=200):
        response_dict = MyBaseSchema(data=data, code=code, message=message).dict()
        super(MyBaseResponse, self).__init__(content=response_dict, status_code=status_code)

