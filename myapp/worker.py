from uvicorn.workers import UvicornWorker


class MyUvicornWorker(UvicornWorker):
    """
    继承uvicorn.workers.UvicornWorker.增加配置项：limit_concurrency，控制并发
    """
    CONFIG_KWARGS = {
        "loop": "uvloop",
        "http": "httptools",
        "limit_concurrency": 10
    }