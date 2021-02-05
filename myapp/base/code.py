class Code(object):
    """
    code有4部分组成，中间以_分割，比如：API_200_000_9999
    第一部分：字符串，标识是API类型还是其他类型。目前只有API,未来可能有SOCKET等其他类型
    第二部分：3位，HTTP code， 比如200，400，500
    第三部分：3位，业务编号，比如000标识系统统一编号，001标识桌面，002标识用户
    第四部分：4位，错误码，比如0000标识未知错误，0001标识参数校验失败
    """
    code_type = "API"
    code_business = "000"  # 标识系统统一编号
    code_error = "0000"  # 标识未知错误


class ErrorCode(Code):
    def __init__(self):
        self.INTERNAL_ERROR = self.code_type + "_500_" + self.code_business + "_0000"  # 未知错误
        self.REQUEST_VALIDATE_ERROR = self.code_type + "_422_" + self.code_business + "_0001"  # request参数校验失败
        self.NOT_FOUND_ERROR = self.code_type + "_404_" + self.code_business + "_0002"  # 资源不存在
        self.UNAUTHORIZED_ERROR = self.code_type + "_401_" + self.code_business + "_0003"  # 没有提供正确的token


class SuccessCode(Code):
    def __init__(self):
        self.SUCCESS = Code.code_type + "_200_" + self.code_business + "_9999"
