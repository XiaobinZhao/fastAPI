import datetime

from myapp.conf.config import settings
from myapp.base.context import request_id_var


class Rotator:
    def __init__(self, *, size, at):
        now = datetime.datetime.now()

        self._size_limit = size
        self._time_limit = now.replace(hour=at.hour, minute=at.minute, second=at.second)

        if now >= self._time_limit:
            # The current time is already past the target time, so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message, file):
        file.seek(0, 2)  # 移动到文件末尾
        if file.tell() + len(message) > self._size_limit:  # 从文章开头到末尾+message的字符个数是否大于限制
            return True
        excess = message.record["time"].timestamp() - self._time_limit.timestamp()
        if excess >= 0:
            elapsed_days = datetime.timedelta(seconds=excess).days
            self._time_limit += datetime.timedelta(days=elapsed_days + 1)
            return True
        return False


def request_id_filter(record):
    record['request_id'] = request_id_var.get()
    return True  # bool,表示是否展示这一条日志记录


# Rotate file if over 20 MB or at midnight every day
rotator = Rotator(size=2e+7, at=datetime.time(0, 0, 0))
log_format = "{time:YYYY-MM-DD HH:mm:ss,SSS}:{level: <8}[{thread}:{process}:{request_id}]" \
             "({module}:{function}:{line: >3}) - {message}"

config = {
    "handlers": [
        # {"sink": sys.stdout, "format": log_format, "level": settings.default.log_level},  # 打开注释可以进行控制台输出
        {"sink": settings.default.log_path,
         "format": log_format,
         "level": settings.default.log_level,
         # "rotation": rotator.should_rotate,  # Automatically rotate too big file
         # "rotation": "10:11",  # Automatically rotate too big file
         # "retention": "1 week",  # Cleanup after some time
         # "compression": "gz",  # Save some loved space
         "colorize": True,  # 开启颜色显示
         "backtrace": True,  # 是否输出整个堆栈，异常向上扩展
         "diagnose": True,  # 堆栈是否打印出变量来更方便debug,可能会有敏感信息被输出
         "enqueue": True,  # 在进入日志文件之前先进行排队，在多进程时有用,
         "filter": request_id_filter
         }

    ]
}
