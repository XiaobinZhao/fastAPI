from enum import Enum

FILES_STATIC_PATH = 'resources'
FILES_TEMPLATE_PATH = 'templates'
TEST_SERVER_NAME = 'testserver'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
TRIAL_SERVICE_UUID = "89b5363ffee04c699f69ec3905079f7f"


class MyBaseEnum(Enum):
    def __str__(self):
        # 重写转为字符串
        return str(self._value_)

    def __repr__(self):
        # 重写实例化输出
        return str(self._value_)


class LogStatusEnum(str, MyBaseEnum):
    # 'success', 'fail', 'unknown'
    success = "success"
    fail = "fail"
    unknown = "unknown"


class EnabledEnum(str, MyBaseEnum):
    enabled = "enabled"
    disabled = "disabled"


class UserTypeEnum(str, MyBaseEnum):
    admin = "admin"
    user = "user"


class LogResourceAppTypeEnum(str, MyBaseEnum):
    ios = "ios"
    android = "android"
    web = "web"
