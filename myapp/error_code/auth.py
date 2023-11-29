from myapp.base.code import ErrorCode as ErrorCodeBase
from myapp.base.code import InfoCode as InfoCodeBase
from myapp.base.code import SuccessCode as SuccessCodeBase
from myapp.base.code import WarningCode as WarningCodeBase


class Code:
    def __init__(self):
        pass

    code_business = "004"  # 业务编号


class ErrorCode(Code, ErrorCodeBase):
    @classmethod
    def SECRET_REQUEST_INVALID_ERROR(cls):
        # 加密传参结构异常
        _code = cls.code_level + cls.code_type + "_400_" + cls.code_business + "_0104"
        _zh = "请求数据结构异常，不能被json序列化"
        _en = "The request data for nonce token invalid."
        return {"code": _code, "zh": _zh, "en": _en}

    @classmethod
    def SIGNATURE_VERIFICATION_ERROR(cls):
        # 签名验证错误，可能是header上签名字段格式不正确/缺失等
        _code = cls.code_level + cls.code_type + "_401_" + cls.code_business + "_0107"
        _zh = "签名验证失败"
        _en = "Signature verification failed."
        return {"code": _code, "zh": _zh, "en": _en}

    @classmethod
    def UNAUTHORIZED_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_401_" + cls.code_business + "_0112"  # 没有提供正确的token
        _zh = "认证失败, token不合法"
        _en = "authentication failed, token is invalid"
        return {"code": _code, "zh": _zh, "en": _en}


class SuccessCode(Code, SuccessCodeBase):
    pass


class WarningCode(Code, WarningCodeBase):
    pass


class InfoCode(Code, InfoCodeBase):
    pass
