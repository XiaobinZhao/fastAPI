from fastapi import status
from myapp.code.desktop import ErrorCode

from myapp.base.exception import MyBaseException


class DesktopNotFountException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.NOT_FOUND_ERROR()["code"]
        keys["message"] = keys.get("message") or "Desktop not found"
        keys["status_code"] = keys.get("status_code") or status.HTTP_404_NOT_FOUND
        super(DesktopNotFountException, self).__init__(*args, **keys)
