from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import InfoCode as InfoCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase
from myapp.base.code import WarningCode as WarningCodeBase


class Code:
    def __init__(self):
        pass

    code_business = "007"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):
    @classmethod
    def I18N_EXIST_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_500_" + cls.code_business + "_0103"
        _zh = "i18n文件不存在"
        _en = "The i18n file does not exist"
        return {"code": _code, "zh": _zh, "en": _en}


class SuccessCode(Code, SuccessCodeBase):
    pass


class WarningCode(Code, WarningCodeBase):
    pass


class InfoCode(Code, InfoCodeBase):
    pass
