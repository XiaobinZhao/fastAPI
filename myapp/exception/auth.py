from starlette import status

from myapp.base.exception import MyBaseException
from myapp.code.auth import ErrorCode


class RequestSecretInvalidException(MyBaseException):
    """
    加密传参结构异常
    """
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.SECRET_REQUEST_INVALID_ERROR()["code"]
        keys["message"] = keys.get("message") or "The request data is invalid."
        keys["status_code"] = keys.get("status_code") or status.HTTP_400_BAD_REQUEST
        super(RequestSecretInvalidException, self).__init__(*args, **keys)


class SignatureVerificationError(MyBaseException):
    """
    签名验证错误，可能是header上签名字段格式不正确/缺失等
    """
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.SIGNATURE_VERIFICATION_ERROR()["code"]
        keys["message"] = keys.get("message") or "Signature verification failed."
        keys["status_code"] = keys.get("status_code") or status.HTTP_401_UNAUTHORIZED
        super(SignatureVerificationError, self).__init__(*args, **keys)


class UnauthorizedException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.UNAUTHORIZED_ERROR()["code"]
        keys["message"] = keys.get("message") or "Could not validate credentials"
        keys["status_code"] = keys.get("status_code") or status.HTTP_401_UNAUTHORIZED
        super(UnauthorizedException, self).__init__(*args, **keys)
