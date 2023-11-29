import random
import string
import pytz
from datetime import datetime

from myapp.base.constant import TIME_FORMAT


def singleton(cls):
    import threading

    _instance = {}
    _instance_lock = threading.Lock()  # 作用是保证多线程下依然保证唯一性

    def _singleton(*args, **kargs):
        with _instance_lock:
            if cls not in _instance:
                _instance[cls] = cls(*args, **kargs)
            return _instance[cls]

    return _singleton


def get_base_classes_recursive(specified_class, base_class_result=(), stop_name="object"):
    """
    递归查找指定class的基类，直到遇到预设的class name(默认object)
    :param specified_class: 指定的class
    :param stop_name: 预设的停止递归的class name
    :param base_class_result: 返回的最后结果
    :return: List<object> 指定class的基类的列表
    """
    base_classes = specified_class.__bases__
    for base in base_classes:
        base_name = base.__name__
        if base_name != stop_name:
            base_class_result.append(base)
        elif base_name == "object":
            base_class_result.append(object)
            return base_class_result
    return get_base_classes_recursive(base, base_class_result, stop_name)


def get_random_code(length, is_letter=False):
    """
    length 验证码位数
    is_letter 是否加入大小写字母
    """
    letters = string.ascii_letters
    digits = string.digits
    character = digits
    if is_letter:
        character = letters + digits
    return "".join([random.choice(character) for _ in range(length)])


def format_utc_time(date_time: datetime):
    utc_timezone = pytz.timezone('UTC')
    utc_time = date_time.astimezone(utc_timezone)
    return utc_time.strftime(TIME_FORMAT)
