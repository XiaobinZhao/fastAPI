class Code:
    pass


class ErrorCode(Code):
    INTERNAL_ERROR = "API_0000"  # 未知错误
    REQUEST_VALIDATE_ERROR = "API_0001"  # request参数校验失败
    NOT_FOUND_ERROR = "API_0002"  # 资源不存在


class SuccessCode(Code):
    SUCCESS = "API_9999"


