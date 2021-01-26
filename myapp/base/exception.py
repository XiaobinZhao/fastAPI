from fastapi import HTTPException
from fastapi import status
from myapp.base import code


class MyBaseException(HTTPException):
    """
    exception 基类，未知异常错位码为0001
    """
    def __init__(self, code=code.ErrorCode.INTERNAL_ERROR, message="", data={},
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.code = code
        self.message = message
        self.data = data
        self.status_code = status_code
        super(MyBaseException, self).__init__(self.status_code, self.message)


class NotFountException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or code.ErrorCode.NOT_FOUND_ERROR
        keys["message"] = keys.get("message") or "resource not found"
        keys["status_code"] = keys.get("status_code") or status.HTTP_404_NOT_FOUND
        super(NotFountException, self).__init__(*args, **keys)
