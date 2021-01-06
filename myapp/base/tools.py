import base64
import time
from datetime import datetime
from loguru import logger


def decrypt(data="admin"):
    """
    rsa 解密.密文是先使用 rsa公钥加密之后在使用base64转码。
    所以解密过程为逆序：先base64解码在rsa私钥解密

    由于前端使用jsencrypt(js) encrypt，python解析时可能会出错，具体参看：
    https://stackoverflow.com/questions/57035263/jsencryptjs-encrypt-but-python-cannot-decrypt
    https://github.com/travist/jsencrypt/issues/158
    解决方案是：padded to the length of the modulus with leading 0x00 values
    """
    from urllib import parse
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP

    data = parse.unquote(data)
    after_b64_decode = base64.b64decode(data)
    if len(after_b64_decode) == 127:
        hex_fixed = '00' + after_b64_decode.hex()
        after_b64_decode = base64.b16decode(hex_fixed.upper())
    private_key_file = "/root/workspace/fastApi/myapp/conf/rsa/private_key.pem"
    with open(private_key_file, 'r') as f:
        key = f.read()
        rsa_key = RSA.import_key(key)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)
        encrypted_data = cipher_rsa.decrypt(after_b64_decode)
        return encrypted_data.decode("utf-8")


def encrypt(data):
    """
    RSA加密.再转成base64
    """
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_OAEP

    public_key_location = "/root/workspace/fastApi/myapp/conf/rsa/public_key.pem"
    with open(public_key_location, "r") as f:
        key = f.read()
        rsa_key = RSA.import_key(key)
        cipher = PKCS1_OAEP.new(rsa_key)
        cipher_text = base64.b64encode(cipher.encrypt(data.encode(encoding="utf-8")))
        # 通过生成的对象加密message明文，注意，在python3中加密的数据必须是bytes类型的数据，不能是str类型的数据
        return cipher_text.decode("utf-8")


def to_datetime(src_time, src_time_fmt=None):
    """
    不同的日期格式转为datetime,如果src_time为空，取当前时间
    :param src_time: 初始的时间信息。可以是一个datetime对象或者是时间戳或者为字符串，如果为字符串需要提供src_time_fmt
    :param src_time_fmt: 初始时间格式
    :return: 返回时间戳
    """
    if src_time:
        if isinstance(src_time, datetime):
            local_time = src_time
        elif isinstance(src_time, int):
            if src_time > 1000000000000:  # 1000000000000 13位，代表2286年以后，正常情况应该是12位长度，所以直接对比数字
                src_time = src_time / 1000
            local_time = datetime.fromtimestamp(src_time)
        else:
            # 字符串时间转为时间戳
            tmp_time = time.mktime(time.strptime(src_time, src_time_fmt))
            # 时间戳转为datetime时间
            local_time = datetime.fromtimestamp(tmp_time)
    else:
        local_time = datetime.fromtimestamp(int(time.time()))
    return local_time


def timestamp_to_str(timestamp, datetime_format=None, timezone=None):
    """
    将时间戳转换为日期时间字符串
    :param timestamp: 待转换的时间戳值
    :param datetime_format: 时间格式
    :param timezone: 时区
    :return: 转换后的带格式字符串
    """
    import pytz

    datetime_format = datetime_format or "%Y-%m-%d %H:%M:%S %Z (%z)"
    if timezone:
        tz = pytz.timezone(timezone)
        return datetime.fromtimestamp(timestamp, tz).strftime(datetime_format)
    else:
        return time.strftime(datetime_format, time.gmtime(timestamp))


def bytes_to_gb(byte):
    """
    将容量单位为bytes（字节）的转为GB
    :param byte: 待转换的字节数
    :return: 转换为GB后的大小（取2位小数）
    """
    return "%.2f" % (int(byte) / 1024 / 1024 / 1024)


def gb_to_bytes(gb):
    """
    将容量单位为GB的转为bytes
    :param gb: 待转换的GB
    :return: 转换为bytes的大小
    """
    return int(gb) * 1024 * 1024 * 1024


def mb_to_gb(mb):
    """
    将容量单位以MB的转换为GB
    :param mb: 待转换的MB
    :return: 转换后的GB值string格式，保留两位小数
    """
    return "%.2f" % (int(mb) / 1024)


def execute_command(command, is_raise_exception=False):
    """
    python执行系统命令
    :param command: 命令内容
    :param is_raise_exception: 是否在执行命令失败时抛出异常，默认抛出异常
            ret_code为执行命令成功与失败的code,0表示成功 其他表示失败
            特例：chrony服务关闭时，查看服务状态ret_code为1，但不想抛出异常，可使用is_raise_exception进行限制
    :return:
    """
    import subprocess

    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret_code = p.wait()
    if ret_code != 0 and is_raise_exception:
        reason = p.stderr.read()
        raise Exception("Execute command %s failed: %s" % (command, reason.decode()))
    result = p.stdout.read()
    return result.decode()


def ip_string_to_int(str_ip):
    import socket
    import struct

    return socket.ntohl(struct.unpack("I", socket.inet_aton(str(str_ip)))[0])


def ip_int_to_string(int_ip):
    import socket
    import struct

    return socket.inet_ntoa(struct.pack('I', socket.htonl(int_ip)))


def generate_random_str(str_length=16, additional_character=""):
    """
    生成一个指定长度的随机字符串
    :param str_length:  随机字符串的长度
    :param additional_character: 来自外部的扩容字符集
    :return: 生成的随机字符串
    """
    import random
    base_character_set = "ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789"
    random_str = ''
    base_str = base_character_set + additional_character
    length = len(base_str) - 1
    for i in range(str_length):
        random_str += base_str[random.randint(0, length)]
    return random_str


def get_md5(data):
    import hashlib
    md5 = hashlib.md5()

    if not isinstance(data, bytes):
        data = data.encode(encoding='utf-8')
    md5.update(data)
    return md5.hexdigest()


def get_local_ip():
    """
    获取本机ip地址
    当有多网卡的时候，如何获取正确的IP地址：
    1. 获取所有启用的网卡
    2. 获取以ens或eth为首命名的网卡
    3. 获取到第一条数据
    :return: 返回本机ip地址
    """
    cmd = "ip r | grep src | grep -v down | grep -E \"ens|eth\" | awk -F \"src\" '{print $2}' | awk " \
          "-F \" \" '{print $1}' | head -n 1"
    ip_address = execute_command(cmd)
    return ip_address.rstrip('\n')


def str_to_base64(string, code_type="utf-8"):
    return base64.b64encode(string.encode(code_type)).decode(code_type)


def test_endpoint(endpoint, timeout=5):
    """
    测试地址是否可用。
    :param endpoint: 类似于 10.221.120.11:8080 这样的地址
    :param timeout: 超时设置。默认5秒
    :return: 测试结果。True表示可用，False表示不可用
    """
    import socket
    from urllib.parse import urlparse

    endpoint = urlparse(endpoint)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    exec_result = sock.connect_ex((endpoint.hostname, endpoint.port if endpoint.port else 80))
    logger.debug("test endpoint: %s, result is: %s" % (endpoint, exec_result))
    sock.close()
    return True if exec_result == 0 else False


def str_signature(key, data):
    import hmac
    from hashlib import sha1

    h = hmac.new(key.encode(), data.encode(), sha1)
    return base64.b64encode(h.digest()).decode()


def generate_request_signature(url, method, access_secret=None):
    """
    使用access secret生成签名
    :param url: 请求的url
    :param method: http method
    :param access_secret: access secret
    :return: (date, signature)
    """
    access_secret = access_secret if access_secret else 'bmvNywOvf2FSRoMwDaCa7vpFM9yM5VFhvisUeD6q'  # 默认 access_secret
    date = str(time.time())
    path = url.split("?")
    message = str(method + "\n" + date + "\n" + path[0])
    # 使用签名验证request是否合法
    signature = str_signature(access_secret, message)
    logger.debug("params of request signature is url:%s, method:%s, access_secret:%s" % (url, method, access_secret))
    return date, signature


def varify_request_signature(signature, request_date, url, method, access_secret=None):
    """
    校验request的signature是否正确。基本思路是按照参数再次做签名，对比前后签名是否一致。
    :param signature: request参数带的签名信息
    :param request_date: request参数的date
    :param url: request 的url
    :param method: request method
    :param access_secret: access secret
    :return: bool，是否校验通过
    """
    url = url.split("?")[0]
    if not url.startswith('/'):
        url = '/' + url

    message = str(method + "\n" + request_date + "\n" + url)
    access_secret = access_secret if access_secret else 'bmvNywOvf2FSRoMwDaCa7vpFM9yM5VFhvisUeD6q'  # 默认 access_secret
    new_signature = str_signature(access_secret, message)
    return new_signature == signature


if __name__ == '__main__':
    encode_str = encrypt("abc")
    assert decrypt(encode_str) == "abc"
    print("[PASS]AES encrypt/decrypt pass")

    now = datetime.fromtimestamp(1609405838)  # 2020-12-31 17:10:38
    assert to_datetime(1609405838) == now
    to_datetime(None)
    assert to_datetime(now) == now
    assert to_datetime("Dec 31, 2020 5:10:38 PM", "%b %d, %Y %I:%M:%S %p") == datetime.fromtimestamp(1609405838)
    print("[PASS]to_datetime pass")

    # 1609405838 2020-12-31 17:10:38
    assert timestamp_to_str(1609405838) == "2020-12-31 09:10:38 GMT (+0000)"
    assert timestamp_to_str(1609405838, datetime_format="%Y-%m-%d %H:%M:%S", timezone="Asia/Shanghai") == "2020-12-31 17:10:38"
    print("[PASS]timestamp_to_str pass")

    assert bytes_to_gb(10000000000) == "9.31"
    print("[PASS]bytes_to_gb pass")

    assert gb_to_bytes(1) == 1073741824
    print("[PASS]gb_to_bytes pass")

    assert mb_to_gb(10000) == "9.77"
    print("[PASS]mb_to_gb pass")

    assert ip_string_to_int("10.221.120.11") == 182286347
    assert ip_int_to_string(182286347) == "10.221.120.11"
    print("[PASS]ip to int pass")

    print(generate_random_str())
    print(generate_random_str(additional_character="正好"))
    print("[PASS]generate_random_str pass")

    assert get_md5("abcd") == "e2fc714c4727ee9395f324cd2e7f331f"
    print("[PASS]get_md5 pass")

    print(get_local_ip())
    print("[PASS]get_local_ip pass")

    assert str_to_base64("abc") == "YWJj"
    print("[PASS]str_to_base64 pass")

    assert test_endpoint("http://127.0.0.1:80")
    print("[PASS]test_endpoint pass")

    date, h = generate_request_signature("/desktops", "GET", )
    assert varify_request_signature(h, date, "/desktops", "GET")
    print("[PASS]request signature pass")
