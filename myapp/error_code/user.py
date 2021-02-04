from myapp.base.code import ErrorCode
from myapp.base.code import SuccessCode


class ErrorCode(ErrorCode):
    USER_LOGIN_NAME_EXIST_ERROR = "API_2001"  # 登录名重复


class SuccessCode(SuccessCode):
    pass
