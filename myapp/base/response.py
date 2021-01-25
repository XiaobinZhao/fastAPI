from fastapi.responses import JSONResponse
from myapp.base.schema import ResponseModel


class MyBaseResponse(JSONResponse):
    def __init__(self, code, message="", data={}, status_code=200):
        response_dict = ResponseModel(data=data, code=code, message=message).dict()
        super(MyBaseResponse, self).__init__(content=response_dict, status_code=status_code)
