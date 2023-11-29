import json
import pathlib

from loguru import logger

from myapp.exception.system import I18nNotExistsException


class SystemManager(object):
    def __init__(self, *args, **keywords):
        super(SystemManager, self).__init__(*args, **keywords)

    @staticmethod
    async def get_i18n_collection():
        root_path = pathlib.Path(__file__).parent.parent.resolve()  # 使用绝对路径，防止环境不同导致的异常
        zh_file_path = root_path.joinpath("i18n/zh.json")
        en_file_path = root_path.joinpath("i18n/en.json")
        try:
            with open(zh_file_path, 'r') as file:
                zh_data = json.load(file)
            with open(en_file_path, 'r') as file:
                en_data = json.load(file)
        except OSError:
            raise I18nNotExistsException()
        return {"zh": zh_data, "en": en_data}

    @staticmethod
    async def get_gateway():
        """
        返回系统当前网关
        """
        try:
            from eojo.main import root_path
            gateway_path = root_path.parent.joinpath("gateway.txt")
            with open(gateway_path, 'r') as file:
                gateway = file.read().rstrip()
        except Exception as e:
            logger.error(str(e))
            gateway = ""
        return gateway
