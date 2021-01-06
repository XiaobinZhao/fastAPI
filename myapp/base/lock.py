import time
import uuid
import redis
from functools import wraps
from oslo_concurrency import lockutils


class BaseLock(object):
    """
    本锁可用于单机内多进程、多线程之间的同步，如果锁名相同，则同一时间内只会有一个线程在执行。

    目前实现了oslo、redis、etcd三种锁，经测试（test_case中的test_lock接口）：QPS如下：
    oslo(625) > redis(160) > etcd(64)

    示例：
    @ProcessThreadLock(lock_name=ResourceLock.SPICE.value, prefix_or_path=ResourceLock.LOCK_FILE_PATH.value)
    def check_max_concurrency(self, desktop_attached_gpu, client_uuid):
       ...

    @ProcessThreadLock(lock_type='etcd', lock_name='desktop', host=etcd_conf['host'], port=2379,
                      username=etcd_conf['user'], password=etcd_conf['password'],
                      prefix_or_path='/var/locks')
    def check_max_concurrency(self, desktop_attached_gpu, client_uuid):
       ...

    @ProcessThreadLock(lock_type='redis', lock_name='desktop', host='localhost', port=6379,
                      password='7a38d7c46ca4798c7767')
    def check_max_concurrency(self, desktop_attached_gpu, client_uuid):
       ...

    由于etcd需要安装etcd client ，代码暂时去除。需要的话请自行安装。本代码使用的是python-etcd==0.4.5.
    """
    def __init__(self, lock=None, lock_name='', host='localhost', port=None,
                 username=None, password=None, prefix_or_path='/var/locks'):
        """
        :param lock: 锁（客户端）实例
        :param lock_name: 锁名称
        :param host: 锁（客户端）主机
        :param port:锁（客户端）端口
        :param username:锁（客户端）用户名
        :param password:锁（客户端）密码
        :param prefix_or_path:锁路径
        """
        self.lock = lock
        self.lock_name = lock_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.prefix_or_path = prefix_or_path

    def _acquire(self, acquire_timeout):
        """
        加锁
        """
        raise NotImplementedError

    def _release(self, identifier):
        """
        释放锁
        """
        raise NotImplementedError

    def lock_warp(self, acquire_timeout=60):
        """
        锁装饰器
        :param acquire_timeout: 申请锁时等待超时时间
        :return:
        """
        def decorator(func):
            @wraps(func)
            def wrap(*args, **kwargs):
                identifier = self._acquire(acquire_timeout)
                if not identifier:
                    raise Exception('Acquire lock timeout')
                try:
                    return func(*args, **kwargs)
                finally:
                    self._release(identifier)
            return wrap
        return decorator


# class EtcdLock(BaseLock):
#     """
#     ETCD锁
#     """
#     def __init__(self, lock=None, lock_name='', host='localhost', port=2379,
#                  username=None, password=None, prefix_or_path='/var/locks'):
#         port = port if port else 2379
#         super(EtcdLock, self).__init__(
#             lock, lock_name, host, port,
#             username, password, prefix_or_path)
#         if isinstance(lock, etcd.Client):
#             self.client = lock
#         else:
#             self.client = etcd.Client(
#                 host=host, port=port,
#                 username=username,
#                 password=password,
#                 lock_prefix=prefix_or_path
#             )
#
#     def lock_warp(self, acquire_timeout=60):
#         def decorator(func):
#             @wraps(func)
#             def wrap(*args, **kwargs):
#                 with etcd.Lock(self.client, self.lock_name) as my_lock:
#                     rst = func(*args, **kwargs)
#                     my_lock.acquire(lock_ttl=acquire_timeout)
#                     return rst
#             return wrap
#         return decorator


class OsloLock(BaseLock):
    """
    OSLO锁
    """
    def lock_warp(self, acquire_timeout=60):
        return lockutils.synchronized(self.lock_name, external=True, lock_path=self.prefix_or_path)


class RedisLock(BaseLock):
    """
    redis 锁
    """
    def __init__(self, lock=None, lock_name='', host='localhost',
                 port=6379, username=None, password=None, prefix_or_path='/var/locks'):
        port = port if port else 6379
        lock_name = prefix_or_path + lock_name
        super(RedisLock, self).__init__(
            lock, lock_name, host, port,
            username, password, prefix_or_path
        )
        if isinstance(lock, redis.Redis):
            self.lock = lock
        else:
            self.lock = redis.Redis(
                host=host,
                port=port,
                password=password
            )

    def _acquire(self, acquire_timeout=60):
        """
        基于 Redis 实现的分布式锁
        :param acquire_timeout: 获取锁的超时时间，默认 60 秒
        :return:
        """
        identifier = str(uuid.uuid4())
        end = time.time() + acquire_timeout
        while time.time() < end:
            if self.lock.set(self.lock_name, identifier, nx=True):
                return identifier
            time.sleep(0.001)
        return False

    def _release(self, identifier):
        """
        释放锁，原子操作
        :param identifier: 锁的标识
        :return:
        """
        unlock_script = """
        if redis.call("get",KEYS[1]) == ARGV[1] then
            return redis.call("del",KEYS[1])
        else
            return 0
        end
        """
        unlock = self.lock.register_script(unlock_script)
        unlock(keys=[self.lock_name], args=[identifier])


class ProcessThreadLock(object):
    """
    单机进程线程锁 装饰器类
    """
    LOCK_TYPES = {
        'oslo': OsloLock,
        'redis': RedisLock
        # 'etcd': EtcdLock
    }

    def __init__(self, lock_type='oslo', lock=None, lock_name='',
                 host='localhost', port=None, username=None, password=None,
                 acquire_timeout=60, prefix_or_path='/var/locks'):
        self.lock_type = lock_type
        self.lock = lock
        self.lock_name = lock_name
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.acquire_timeout = acquire_timeout
        self.prefix_or_path = prefix_or_path

    def __call__(self, func, *args, **kwargs):
        Lock = self.LOCK_TYPES.get(self.lock_type)
        if Lock:
            lock = Lock(self.lock, self.lock_name, self.host, self.port,
                        self.username, self.password, self.prefix_or_path)
        else:
            raise Exception('Cannot found matched lock!')

        @lock.lock_warp(self.acquire_timeout)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper


def test_case():
    import bottle

    r = redis.Redis(password='7a38d7c46ca4798c7767')
    app = application = bottle.Bottle()

    key = 'test_count'
    r.set(key, 0)

    etcd_conf = {
        'host': '127.0.0.1',
        'port': 2379,
        'user': 'root',
        'password': '7a38d7c46ca4798c7767',
        'version_path': '/opt/xview/xview-api/xview/db/etcd/version/'
    }

    # etcd_client = etcd.Client(
    #     host=etcd_conf['host'], port=etcd_conf['port'],
    #     username=etcd_conf['user'], password=etcd_conf['password'],
    #     lock_prefix='/var/locks'
    # )

    @app.route('/test_lock')
    # @ProcessThreadLock(lock_type='oslo', lock=r, lock_name='desktop')  # oslo 锁
    # @ProcessThreadLock(lock_type='etcd', lock=etcd_client, lock_name='desktop')  # etcd传入一个session
    # @ProcessThreadLock(lock_type='etcd', lock_name='desktop', host=etcd_conf['host'], port=2379,
    #                    username=etcd_conf['user'], password=etcd_conf['password'],
    #                    prefix_or_path='/var/locks')  # etcd多session
    @ProcessThreadLock(lock_type='redis', lock=r, lock_name='desktop')  # redis传入一个session
    # @ProcessThreadLock(lock_type='redis', lock_name='desktop', host='localhost', port=6379,
    #                    password='7a38d7c46ca4798c7767')  # redis多session
    def test_lock():
        """
        锁测试
        """
        count = int(r.get(key))
        # time.sleep(0.001)  # 目的阻塞CPU，提高下一行代码争抢CPU概率
        r.set(key, count + 1)
        count = r.get(key)
        print('-------- %s ----------' % count)
        return 'count=%s' % count

    @app.route('/test_lock2')
    def test_lock2():
        def aaa(a, b):
            """
            锁测试
            """
            print(a, b)
            count = int(r.get(key))
            time.sleep(0.001)  # 目的阻塞CPU，提高下一行代码争抢CPU概率
            r.set(key, count + 1)
            count = r.get(key)
            return 'count=%s' % count
        return ProcessThreadLock(lock_type='oslo', lock_name='desktop')(aaa)(1, 2)

    def uwsgi_main():
        """
        使用uwsgi作为server

        uwsgi.ini文件内容如下
        [uwsgi]
        chdir = /home/sihua/test/uwsgi_web
        http = 127.0.0.1:9111
        master = true
        worker = 4
        wsgi-file=process_thread_lock.py
        callable=application
        enable-threads = true
        py-autoreload= 1
        processes = 8
        threads = 8
        daemonize = /home/sihua/test/uwsgi_web/run.log
        """
        app.run()

    def gunicorn_main():
        """
        使用qunicorn作为server，开启多进程多线程，线程不会立即就绪，根据需要开启
        """
        app.run(host='127.0.0.1', port=9111, server='gunicorn',
                worker_class='gevent', workers=8)  # 多进程多线程，process=4， thread=4

    # uwsgi_main()
    gunicorn_main()


if __name__ == '__main__':
    test_case()





