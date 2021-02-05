from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase


class Code:
    code_business = "002"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):

    def __init__(self, status):
        super(ErrorCode, self).__init__()
        self.USER_LOGIN_NAME_EXIST_ERROR = self.code_type + "_" + str(status) + "_" + self.code_business + "_0100"  # 登录名重复


class SuccessCode(Code, SuccessCodeBase):
    pass
