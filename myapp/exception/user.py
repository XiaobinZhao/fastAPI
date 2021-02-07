from fastapi import status
from myapp.base.exception import MyBaseException
from myapp.error_code.user import ErrorCode


class UserLoginNameExistException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode(status.HTTP_409_CONFLICT).USER_LOGIN_NAME_EXIST_ERROR
        keys["message"] = keys.get("message") or "User login name already exists."
        keys["status_code"] = keys.get("status_code") or status.HTTP_409_CONFLICT
        super(UserLoginNameExistException, self).__init__(*args, **keys)


class UserNotFountException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode(status.HTTP_404_NOT_FOUND).NOT_FOUND_ERROR
        keys["message"] = keys.get("message") or "User not found"
        keys["status_code"] = keys.get("status_code") or status.HTTP_404_NOT_FOUND
        super(UserNotFountException, self).__init__(*args, **keys)
