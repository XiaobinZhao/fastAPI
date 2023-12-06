from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import InfoCode as InfoCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase
from myapp.base.code import WarningCode as WarningCodeBase


class Code:
    def __init__(self):
        pass

    code_business = "003"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):
    pass


class SuccessCode(Code, SuccessCodeBase):
    pass


class WarningCode(Code, WarningCodeBase):
    pass


class InfoCode(Code, InfoCodeBase):
    pass
