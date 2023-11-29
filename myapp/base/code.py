class Code(object):
    """
    code有4部分组成，中间以_分割，比如：API_200_000_9999
    第一部分：字符串，标识是API类型还是其他类型。目前只有API,未来可能有SOCKET等其他类型
    第二部分：3位，HTTP code， 比如200，400，500
    第三部分：3位，业务编号，比如000标识系统统一编号，001标识桌面，002标识用户
    第四部分：4位，错误码，比如 0000 标识未知错误，0001标识参数校验失败
    """
    code_type = "API"
    code_business = "000"  # 标识系统统一编号
    code_error = "0000"  # 标识未知错误
    code_success = "9999"


class ErrorCode(Code):
    # 类型用于前端分辨错误信息类型
    code_level = 'ERROR_'

    @classmethod
    def INTERNAL_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_500_" + cls.code_business + "_0000"  # 未知错误
        _zh = "未知系统错误"
        _en = "internal error"
        return {"code": _code, "zh": _zh, "en": _en}

    @classmethod
    def REQUEST_VALIDATE_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_422_" + cls.code_business + "_0001"  # request参数校验失败
        _zh = "request 请求参数校验失败，请检查参数格式"
        _en = "request validation error，please check your parameters"
        return {"code": _code, "zh": _zh, "en": _en}

    @classmethod
    def NOT_FOUND_ERROR(cls):
        _code = cls.code_level + cls.code_type + "_404_" + cls.code_business + "_0002"  # 资源不存在
        _zh = "请求的资源不存在"
        _en = "the request resource not exist"
        return {"code": _code, "zh": _zh, "en": _en}


class SuccessCode(Code):
    code_level = 'SUCCESS_'

    @classmethod
    def SUCCESS(cls):
        _code = cls.code_level + cls.code_type + "_200_" + cls.code_business + f"_{cls.code_success}"
        _zh = "成功"
        _en = "success"
        return {"code": _code, "zh": _zh, "en": _en}


class WarningCode(Code):
    code_level = 'WARNING_'

    @classmethod
    def WARNING(cls):
        _code = cls.code_level + cls.code_type + "_200_" + cls.code_business + f"_{cls.code_success}"
        _zh = "警告"
        _en = "warning"
        return {"code": _code, "zh": _zh, "en": _en}


class InfoCode(Code):
    code_level = 'INFO_'

    @classmethod
    def INFO(cls):
        _code = cls.code_level + cls.code_type + "_200_" + cls.code_business + f"_{cls.code_success}"
        _zh = "提示"
        _en = "info"
        return {"code": _code, "zh": _zh, "en": _en}
