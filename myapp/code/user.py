from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase
from myapp.base.code import WarningCode as WarningCodeBase
from myapp.base.code import InfoCode as InfoCodeBase


class Code:
    code_business = "002"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):

    @classmethod
    def USER_LOGIN_NAME_EXIST_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_409_" + cls.code_business + "_0100"  # 登录名重复
        _zh = "用户登录名不能重复"
        _en = "the user login name cannot be duplicated"
        return {"code": _code, "zh": _zh, "en": _en}


class SuccessCode(Code, SuccessCodeBase):
    pass


class WarningCode(Code, WarningCodeBase):
    pass


class InfoCode(Code, InfoCodeBase):
    pass
