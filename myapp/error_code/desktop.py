from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase


class Code:
    code_business = "001"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):
    pass


class SuccessCode(Code, SuccessCodeBase):
    pass
