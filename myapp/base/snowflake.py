"""
雪花算法：https://github.com/twitter-archive/snowflake
参考：https://github.com/cablehead/python-snowflake
     https://github.com/falcondai/python-snowflake
     https://zhuanlan.zhihu.com/p/85837641  其中的python写法
其核心思想是：
- 第一位 占用1bit，其值始终是0，没有任何意义。在计算机的表示中，第一位是符号位，0表示整数，第一位如果是1则表示负数，我们用的ID默认就是正数，所以默认就是0，那么这一位默认就没有意义。
- 时间戳占用41位，具体到毫秒，41位的二进制可以使用69年，因为时间理论上永恒递增，所以根据这个排序是可以的。
- 机器标识占用10位，可以全部用作机器ID，也可以用来标识机房ID + 机器ID，10位最多可以表示1024台机器。
- 递增计数序列号占用12位，也就是同一台机器上同一时间，理论上还可以同时生成不同的ID。每个节点每毫秒从0开始不断累加，最多可以累加到4095，一共可以产生4096个ID。

雪花算法的优点
- 有业务含义，并且可自定义。 雪花算法的 ID 每一位都有特殊的含义，我们从 ID 的不同位数就可以推断出对应的含义。此外，我们还可根据自身需要，自行增删每个部分的位数，从而实现自定义的雪花算法。
- ID 单调增加，有利于提高写入性能。 雪花算法的 ID 最后部分是递增的序列号，因此其生成的 ID 是递增的，将其作为数据库主键 ID 时可以实现顺序写入，从而提高写入性能。
- 不依赖第三方系统。 雪花算法的生成方式，不依赖第三方系统或中间件，因此其稳定性较高。
- 解决了安全问题。 雪花算法生成的 ID 是单调递增的，但其递增步长又不是确定的，因此无法从 ID 的差值推断出生成的数量，从而可以保护业务隐私。

雪花算法的缺点
- 强依赖机器时间

雪花算法的一些问题处理
1. 69年时限问题
由于算法中用长度41位来表示时间戳，我们的时间计算通常是从1970年开始的，只能使用69年，为了不浪费，其实我们可以用时间的相对值，也就是以项目开始的时间为基准时间，往后可以使用69年，比如现在是2023年，那么往后推69年，就可以使用到2092年。获取唯一ID的服务，对处理速度要求比较高，所以我们全部使用位运算以及位移操作。
2. 时间回拨问题
在获取时间的时候，可能会出现`时间回拨`的问题，什么是时间回拨问题呢？就是服务器上的时间突然倒退到之前的时间。
1. 人为原因，把系统环境的时间改了。
2. 有时候不同的机器上需要同步时间，可能不同机器之间存在误差，那么可能会出现时间回拨问题。

解决方案
- 回拨时间小的时候，不生成 ID，循环等待到时间点到达。
- 上面的方案只适合时钟回拨较小的，如果间隔过大，阻塞等待，肯定是不可取的，因此
  - 要么超过一定大小的回拨直接报错，拒绝服务，
  - 另一种方案是利用拓展位，回拨之后在拓展位上加1就可以了，这样ID依然可以保持唯一。但是这个要求我们提前预留出位数，要么从机器id中，要么从序列号中，腾出一定的位，在时间回拨的时候，这个位置 `+1`。

myapp 的雪花算法
结合以上理论知识，以及myapp项目的情况，64位做一下调整

- 首位不变，保持为0
- 时间戳占用41位，具体到毫秒，
- 机器标识占用8位，其中数据中心1位，机器id 7位
- 时间回拨占用2位
- 递增计数序列号占用12位
所以结构为
0{41-时间戳}{1-数据中心}{7-机器id}{2-时间回拨}{12-递增计数序列号}
"""
import os
import pathlib
import time

from loguru import logger

from myapp.conf.config import settings

# 64位ID的划分，其中有22位自由分配
WORKER_ID_BITS = 7  # 机器标识，7bit
DATACENTER_ID_BITS = 1  # 数据中心，1bit
FIX_SYSTEM_CLOCK_BITS = 2  # 时间回拨拓展位，2bit
SEQUENCE_ID_BITS = 12  # 累计序列号，12bit

# 最大取值计算
MAX_WORKER_ID = -1 ^ (-1 << WORKER_ID_BITS)  # 最大机器数，2**7-1 0b1111111, 0b代表正数，-0b代表负数
MAX_DATACENTER_ID = -1 ^ (-1 << DATACENTER_ID_BITS)  # 最大数据中心，2**1-1 0b1
MAX_FIX_SYSTEM_CLOCK = -1 ^ (-1 << FIX_SYSTEM_CLOCK_BITS)  # 最大支持的时钟回拨次数，2**2-1 0b11
SEQUENCE_MASK = MAX_SEQUENCE_ID = -1 ^ (-1 << SEQUENCE_ID_BITS)  # 最大序列号，2**12-1， 总共可以表示4096个ID

# 移位偏移计算
WORKER_ID_SHIFT = SEQUENCE_ID_BITS
FIX_SYSTEM_CLOCK_SHIFT = SEQUENCE_ID_BITS + FIX_SYSTEM_CLOCK_BITS
DATACENTER_ID_SHIFT = SEQUENCE_ID_BITS + FIX_SYSTEM_CLOCK_BITS + WORKER_ID_BITS
TIMESTAMP_LEFT_SHIFT = SEQUENCE_ID_BITS + FIX_SYSTEM_CLOCK_BITS + WORKER_ID_BITS + DATACENTER_ID_BITS

# 开始时间截 (2023-01-01)
TWEPOCH = 1672531200000
root_path = pathlib.Path(__file__).parent.parent.resolve()  # 使用绝对路径，防止环境不同导致的异常


class SnowflakeGenerator(object):
    """
    用于生成IDs
    """
    def __init__(self, datacenter_id, worker_id, sequence=0, fix_system_clock=0):
        """
        初始化
        :param datacenter_id: 数据中心（机器区域）ID
        :param worker_id: 机器ID
        :param sequence: 递增序号
        :param fix_system_clock: 时钟回拨的次数
        """
        if worker_id > MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f'worker_id:{worker_id}越界,支持 0 - {MAX_WORKER_ID}')

        if datacenter_id > MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f'datacenter_id:{datacenter_id}越界,支持 0 - {MAX_DATACENTER_ID}')

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.sequence = sequence
        self.fix_system_clock = fix_system_clock

        self.last_timestamp = self._read_last_timestamp()  # 上次计算的时间戳

        self._save_last_timestamp(self._gen_timestamp())  # 实例启动时写入当前时间

    @staticmethod
    def _save_last_timestamp(_last_timestamp):
        """
        上次的时间戳写入文件
        :return:int timestamp
        """
        file_path = root_path.parent.joinpath("last_timestamp.txt")
        with open(file_path, 'w') as file:  # 覆盖写
            file.write(str(_last_timestamp))

    @staticmethod
    def _read_last_timestamp():
        """
        从文件读取上次的时间戳
        :return:int timestamp
        """
        try:
            version_path = root_path.parent.joinpath("last_timestamp.txt")
            with open(version_path, 'r') as file:
                _last_timestamp = int(file.read().rstrip())
        except Exception as e:
            logger.error(f"读取last_timestamp.txt失败，{str(e)}")
            _last_timestamp = -1  # 默认值为-1，则一定可以生成
        return _last_timestamp

    @staticmethod
    def _gen_timestamp():
        """
        生成整数时间戳
        :return:int timestamp
        """
        return int(time.time() * 1000)

    def gen_id(self, current_timestamp: int = None):
        """
        获取新ID
        :return:
        """
        timestamp = current_timestamp or self._gen_timestamp()

        if timestamp > self.last_timestamp:
            self.sequence = 0
        else:
            if timestamp < self.last_timestamp:  # 时钟回拨
                self.fix_system_clock = (self.fix_system_clock + 1) & MAX_FIX_SYSTEM_CLOCK
                logger.warning(f"系统时钟回拨，fix_system_clock 加 1： {self.fix_system_clock}")
                if self.fix_system_clock == 0:  # 时钟回拨位到达上限;此时，计数不变，时间等待到下一毫秒，保证id唯一
                    timestamp = self._til_next_millis(self.last_timestamp)

            self.sequence = (self.sequence + 1) & SEQUENCE_MASK
            if self.sequence == 0:  # 序列号到达上限;此时，计数不变，时间等待到下一毫秒，保证id唯一
                timestamp = self._til_next_millis(self.last_timestamp)

        self.last_timestamp = timestamp

        new_id = ((timestamp - TWEPOCH) << TIMESTAMP_LEFT_SHIFT) | (self.datacenter_id << DATACENTER_ID_SHIFT) | \
                 (self.worker_id << WORKER_ID_SHIFT) | self.fix_system_clock << FIX_SYSTEM_CLOCK_SHIFT | self.sequence
        return new_id

    def _til_next_millis(self, last_timestamp):
        """
        等到下一毫秒
        """
        timestamp = self._gen_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._gen_timestamp()
        return timestamp

    def melt(self, snowflake_id, twepoch=TWEPOCH):
        """
        翻译id个部分组成的明文
        """
        sequence_id = snowflake_id & MAX_SEQUENCE_ID
        fix_system_clock_id = (snowflake_id >> SEQUENCE_ID_BITS) & MAX_FIX_SYSTEM_CLOCK
        worker_id = (snowflake_id >> SEQUENCE_ID_BITS >> FIX_SYSTEM_CLOCK_BITS) & MAX_WORKER_ID
        datacenter_id = (snowflake_id >> SEQUENCE_ID_BITS >> FIX_SYSTEM_CLOCK_BITS >> WORKER_ID_BITS) & MAX_DATACENTER_ID
        timestamp_ms = snowflake_id >> SEQUENCE_ID_BITS >> FIX_SYSTEM_CLOCK_BITS >> WORKER_ID_BITS >> DATACENTER_ID_BITS
        timestamp_ms += twepoch

        return timestamp_ms, int(datacenter_id), int(worker_id), int(fix_system_clock_id), int(sequence_id)


def local_datetime(timestamp_ms):
    import datetime
    """convert millisecond timestamp to local datetime object."""
    return datetime.datetime.fromtimestamp(timestamp_ms / 1000)


# 数据中心id由配置文件获取，默认是0
# 机器id取进程id的最后2位
IDWorker = SnowflakeGenerator(settings.default.snowflake_datacenter_id, int(str(os.getpid())[-2:]))


if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor

    def ge_id(*args):
        print(*args)
        for i in range(5):
            t0 = int(time.time() * 1000)
            # if i % 2 == 1:
            #     t0 = int(time.time() * 1000 - 10000)  # 模拟时钟回拨
            _new_id = IDWorker.gen_id(t0)

            print(f"new_id: {_new_id}, 时间：{t0}, id翻译： {IDWorker.melt(_new_id)}")


    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(2):
            executor.submit(ge_id, f"线程{i}")


