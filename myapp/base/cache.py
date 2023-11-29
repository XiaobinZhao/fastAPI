import asyncio
import json
from json.decoder import JSONDecodeError

import redis
import redis.asyncio as aioredis
from loguru import logger

from myapp.conf.config import settings


def format_result(func):
    async def gen_status(*args, **kwargs):
        error, result = None, None
        try:
            if asyncio.iscoroutinefunction(func):  # 判断是否是协程
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            if type(result) in (bytes, str):
                try:
                    result = json.loads(result)
                except JSONDecodeError:
                    if type(result) == bytes:
                        result = str(result, encoding="utf-8")
        except Exception as e:
            error = str(e)
            raise e
        return {'result': result, 'error': error}

    return gen_status


class Cache(object):
    """
    简单内存缓存，使用字典保存数据。
    """

    def __init__(self):
        self._cache = {}

    def get(self, key, data):
        if key in self._cache:
            return self._cache[key]
        else:
            self._cache[key] = data
            return data

    def set(self, key, data):
        self._cache[key] = data

    def remove(self, key):
        self._cache.pop(key)

    def clear(self):
        self._cache.clear()


class RedisCache(Cache):
    """
    封装redis-py的cache类。可以实现cache的get/set/remove方法。
    示例：
        cache = RedisCache()
        cache.set("key", "value", ex=30)  # 存储一个生命周期为30秒的key/value
        cache.get("key")
        cache.remove("key")
    程序启动的时候会加载当前RedisCache，并且初始化ConnectionPool 和redis client，此时尚未有redis 的tcp connection建立。
    调用self.try_connect()会进行tcp 连接，如果正常连接，就回收该连接。这么做是为了在程序启动的时候进行一次redis连接测试
    程序调用get/set/remove时，重新从池内获取连接
    整个应用退出时，关闭所有的socket 连接。
    """

    def __init__(self):
        self._pool = None
        self._redis_client = self.get_client()
        self.try_connect()  # 程序加载即连接redis,如果redis连接失败，直接抛出

    def __del__(self):
        self.close()

    def close(self):
        """
        销毁连接。一般情况下只在整个服务停止的时候才会做。
        :return:
        """
        if self._redis_client:
            self._redis_client = None
        self._pool.disconnect()
        logger.info("Destroy redis cache client success and disconnect all redis tcp connection !")

    def try_connect(self):
        conn = self._pool.get_connection(None)
        self._pool.release(conn)
        logger.info("Redis cache connect keepalive success !")

    def get_client(self):
        if not self._pool:
            self._pool = redis.BlockingConnectionPool(  # 使用线程安全的连接池
                max_connections=50,
                timeout=3,
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.dbid,
                password=settings.redis.password,
                socket_keepalive=True,  # keep alive节省socket创建消耗,默认使用非keepalive
                socket_connect_timeout=1,
                decode_responses=True)
            # redis.ConnectionPool()只是设置了一些如max_connections这些参数，并没有进行redis 的tcp 连接
        _redis_client = redis.Redis(connection_pool=self._pool)
        # redis.Redis()实例只是记录了redis的一些连接参数，依然没有进行tcp连接；只有进行真正的set/get等命令时才会进行tcp 连接

        return _redis_client

    @format_result
    def set(self, key, value, ex=None, px=None, nx=False):
        """
        set data with (key, value)
        :param key:
        :param value:
        :param ex: 过期时间（秒)
        :param px: 过期时间（毫秒)
        :param nx: if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist
        :return:
        """
        return self._redis_client.set(key, value, ex=ex, px=px, nx=nx)

    @format_result
    def get(self, key):
        return self._redis_client.get(key)

    @format_result
    def expire(self, key, time):
        return self._redis_client.expire(key, time)

    @format_result
    def remove(self, key):
        return self._redis_client.delete(key)


class AsyncRedisCache(Cache):
    """
    异步的redis cache
    默认redis会创建连接池处理redis连接。并且在redis实例关闭时自动关闭池内的连接
    """

    def __init__(self):
        super().__init__()
        self._cache = aioredis.from_url(settings.redis.url, decode_responses=True)  # 默认返回bytes; 这里设置默认需要decode

    async def close(self):
        """
        在redis实例关闭时自动关闭池内的连接
        """
        await self._cache.close()

    @format_result
    async def set(self, key, value, ex=None, px=None, nx=False):
        """
        set data with (key, value)
        :param key:
        :param value:
        :param ex: 过期时间（秒)
        :param px: 过期时间（毫秒)
        :param nx: if set to True, set the value at key ``name`` to ``value`` only
            if it does not exist
        :return:
        """
        return await self._cache.set(key, value, ex=ex, px=px, nx=nx)

    @format_result
    async def get(self, key):
        return await self._cache.get(key)

    @format_result
    async def expire(self, key, time):
        return await self._cache.expire(key, time)

    @format_result
    async def remove(self, key):
        return await self._cache.delete(key)


MyCache = AsyncRedisCache()

if __name__ == '__main__':
    async def filter_desktops():
        s = await MyCache.set("xxx", "xxx", ex=20)
        d = await MyCache.get("xxx")  # ConnectClosedError(Reader at end of file)
        f = await MyCache.get("xxx")  # ConnectRefusedError([Errno 111] Connect call failed ('127.0.0.1', 6379))
        g = await MyCache.get("xxx")
        g1 = await MyCache.get("xxx")
        g2 = await MyCache.get("xxx")
        h = await MyCache.get("yyy")
        print(s, d, f, g, g1, g2, h)


    loops = asyncio.get_event_loop()
    loops.run_until_complete(asyncio.wait([filter_desktops()]))
