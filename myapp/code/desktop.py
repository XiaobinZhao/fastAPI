from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import SuccessCode as InfoCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase
from myapp.base.code import SuccessCode as WarningCodeBase


class Code:
    code_business = "001"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):
    pass


class SuccessCode(Code, SuccessCodeBase):
    pass


class WarningCode(Code, WarningCodeBase):
    pass


class InfoCode(Code, InfoCodeBase):
    pass
