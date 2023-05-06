from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase

class Code:
    code_business = '002'	# 业务编号

class ErrorCode(Code, ErrorCodeBase):
    @classmethod
    def QUESTION_LOGIN_NAME_EXIST_ERROR(cls, status):
        _code = cls.code_type + "_" + str(status) + "_" + cls.code_business + "_0100"  # 登录名重复
        _zh = "jjtest 用户登录名不能重复"
        _en = "the user login name cannot be duplicated"
        return {"code": _code, "zh": _zh, "en": _en}