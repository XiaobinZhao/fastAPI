from json import loads as json_loads
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from myapp.conf.config import settings

Model_Base = declarative_base()


def json_serializer(s, **kw):
    if isinstance(s, bytes):
        return json_loads(s.decode('utf-8'), **kw)
    else:
        return json_loads(s, **kw)


DB_Engine = create_engine(settings.db.url,
                          echo=False,
                          echo_pool=True,
                          pool_size=10,  # 池最大连接数
                          max_overflow=10,  # 池最多溢出连接数
                          pool_recycle=600,  # 池回收connection的间隔，默认不回收（-1）。当前为10分钟。
                          pool_timeout=30,  # 从池获取connection的最长等待时间，默认30s
                          json_serializer=json_serializer,
                          poolclass=QueuePool)  # 默认是QueuePool
SessionFactory = sessionmaker(DB_Engine)


class TimestampMixin(object):
    created_at = Column("created_at", TIMESTAMP(), default=datetime.now, nullable=True, comment="创建时间")
    updated_at = Column("updated_at", TIMESTAMP(), default=datetime.now, nullable=True, onupdate=datetime.now,
                        comment="最后修改时间")
