from fastapi import HTTPException
from myapp.base.code import ErrorCode


class MyBaseException(HTTPException):
    """
    exception 基类，未知异常错位码为0001
    """
    def __init__(self, code=ErrorCode.INTERNAL_ERROR, message="", data={}, status_code=500):
        self.code = code
        self.message = message
        self.data = data
        self.status_code = status_code
        super(MyBaseException, self).__init__(self.status_code, self.message)


class NotFountException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["status_code"] = keys.get("status_code") or 404
        keys["message"] = keys.get("message") or "resource not found"
        super(NotFountException, self).__init__(*args, **keys)
