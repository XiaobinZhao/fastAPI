from fastapi import status
from myapp.base import code
from myapp.base.exception import MyBaseException
from myapp.error_code.jjtest import ErrorCode

class QuestionLoginNameExistException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.QUESTION_LOGIN_NAME_EXIST_ERROR(status.HTTP_409_CONFLICT)["code"]
        keys["message"] = keys.get("message") or "Question login name already exists."
        keys["status_code"] = keys.get("status_code") or status.HTTP_409_CONFLICT
        super(QuestionLoginNameExistException, self).__init__(*args, **keys)

class QuestionNotFountException(MyBaseException):
    def __init__(self, *args, **keys):
        keys["code"] = keys.get("code") or ErrorCode.NOT_FOUND_ERROR()["code"]
        keys["message"] = keys.get("message") or "Question not found"
        keys["status_code"] = keys.get("status_code") or status.HTTP_404_NOT_FOUND
        super(QuestionNotFountException, self).__init__(*args, **keys)
