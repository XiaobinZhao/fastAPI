from fastapi import HTTPException
from fastapi import status

from myapp.base import code as base_code


class MyBaseException(HTTPException):
    """
    exception 基类，未知异常错位码为0001
    """

    def __init__(self, code=base_code.ErrorCode.INTERNAL_ERROR()["code"], message="", data=None,
                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **keys):
        self.code = code
        self.message = message
        self.data = data
        self.status_code = status_code
        super(MyBaseException, self).__init__(self.status_code, self.message, **keys)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        # 支持三种转换标志：'!s' 调用 str() , '!r' 调用 repr() ,  '!a' 调用 ascii()。
        # repr(object) 方法是在字符串的外层再套一个引号,返回的是一个对象的 string 格式。
        return f"{class_name}(code={self.code!r}, status_code={self.status_code!r}, message={self.message!r})"

    def __str__(self):
        return self.message + '\n' + super().__str__()


class NotFoundException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or base_code.ErrorCode.NOT_FOUND_ERROR()["code"]
        keys["message"] = keys.get("message") or "resource not found"
        keys["status_code"] = keys.get("status_code") or status.HTTP_404_NOT_FOUND
        super(NotFoundException, self).__init__(*args, **keys)


