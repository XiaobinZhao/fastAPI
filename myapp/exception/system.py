from fastapi import status

from myapp.base.exception import MyBaseException
from myapp.code.system import ErrorCode


class I18nNotExistsException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.I18N_EXIST_ERROR()["code"]
        keys["message"] = keys.get("message") or "The i18n file does not exist."
        keys["status_code"] = keys.get("status_code") or status.HTTP_500_INTERNAL_SERVER_ERROR
        super(I18nNotExistsException, self).__init__(*args, **keys)
