import logging
import sys

from uvicorn.workers import UvicornWorker
from uvicorn.logging import AccessFormatter

from myapp.base.context import request_id_var


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        request_id = request_id_var.get()

        if request_id:
            record.request_id = request_id
        return True


class MyUvicornWorker(UvicornWorker):
    """
    继承uvicorn.workers.UvicornWorker.增加配置项：limit_concurrency，控制并发
    """
    CONFIG_KWARGS = {
        "loop": "uvloop",
        "http": "httptools",
        "limit_concurrency": 10
    }

    def __init__(self, *args, **kwargs):
        super(MyUvicornWorker, self).__init__(*args, **kwargs)

        # 覆盖uvicorn的access log
        fmt = '%(asctime)s %(levelprefix)s [%(request_id)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
        access_logger = logging.getLogger("uvicorn.access")
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(AccessFormatter(fmt))
        handler.addFilter(RequestIdFilter())
        access_logger.handlers = [handler]
