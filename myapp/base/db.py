import inspect
import asyncio
from typing import List, Union
from datetime import datetime
from sqlalchemy import select
from sqlalchemy import TIMESTAMP, Column, and_, desc
from sqlalchemy.pool import QueuePool
from sqlalchemy.engine.result import Result
from sqlalchemy.orm import as_declarative, declared_attr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from myapp.base import json_serializer
from myapp.conf.config import settings

IGNORE_ATTRS = ['redis']
DB_Engine = create_async_engine(settings.db.aiomysql_url,
                                echo=False,
                                echo_pool=True,
                                pool_size=5,  # 池最大连接数
                                max_overflow=10,  # 池最多溢出连接数
                                pool_recycle=600,  # 池回收connection的间隔，默认不回收（-1）。当前为10分钟。
                                pool_timeout=5,  # 从池获取connection的最长等待时间，默认30s,当前 15s
                                json_serializer=json_serializer,
                                poolclass=QueuePool)  # 默认是QueuePool


class PropertyHolder(type):
    """
    使用元类的方式重新构造，使其子类可以知道自己有哪些properties.
    目的是为了实现序列化的时候可以区分异步和同步的属性.
    """
    def __new__(mcs, name, bases, attrs):
        new_cls = type.__new__(mcs, name, bases, attrs)
        new_cls.property_fields = []

        for attr in list(attrs) + sum([list(vars(base))
                                       for base in bases], []):
            if attr.startswith('_') or attr in IGNORE_ATTRS:
                continue
            if isinstance(getattr(new_cls, attr), property):
                new_cls.property_fields.append(attr)
        return new_cls


@as_declarative()
class Base(object):
    __name__: str

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()


class ModelMeta(Base.__class__, PropertyHolder):
    """
    Base是ORM的基类，他本身的元类也被改变（意味着不是type）,如果直接改变它则会让我们的数据类型丧失ORM的功能，
    两全其美的办法是创建一个新的类同时继承Base和PropertyHolder, 使这个类成为新的混合元类.
    """
    ...


class BaseModel(Base, metaclass=ModelMeta):
    """
    SQLAlchemy 1.4 support asynchronous.so, 当前基类同时支持同步和异步查询
    SQLAlchemy的ORM继承，在 `classmethod` 和 `staticmethod` 继承是和Python OOP面向对象的继承方案一致的。
    也就是说：
    被冠之`@staticmethod`的静态方法，会被继承，但是在子类调用的时候，却是调用的父类同名方法。
    被冠之`@classmethod`的类方法，会被继承，子类调用的时候就是调用子类的这个方法。
    """
    # Sqlalchemy的抽象方法的定义，代表BaseModel含有抽象方法，需要被子类继承实现；
    # 另外，抽象方法不需要写__tablename__属性
    __abstract__ = True

    created_at = Column("created_at", TIMESTAMP(), default=datetime.now, nullable=True, comment="创建时间")
    updated_at = Column("updated_at", TIMESTAMP(), default=datetime.now, nullable=True, onupdate=datetime.now,
                        comment="最后修改时间")

    @classmethod
    def results_to_dict(cls, results: Union[Result, List[Result]]) -> Union[List[dict], dict]:
        """
        非ORM方式查询时，对结果是 [sqlalchemy.engine.Result] 类型的结果进行转化
        """
        if not isinstance(results, list):
            return {col: val for col, val in results._mapping.items()}
        list_dct = []
        for row in results:
            dct = {col: val for col, val in row._mapping.items()}  # SQLAlchemy 1.4支持
            list_dct.append(dct)
        return list_dct

    def to_dict(self, except_keys=[]):
        """
        当前model 对象转为字典
        :param except_keys: 不期望返回的字段
        :return: 字典(dict)
        """
        if hasattr(self, "__mapper__"):
            keys = [prop.key for prop in self.__mapper__.iterate_properties]
        else:
            keys = list(vars(self).keys())
        keys = list(set(keys) - set(except_keys))  # 去除不期望返回的字段
        format_data = {}
        for key in keys:
            format_data[key] = getattr(self, key)
            if isinstance(format_data[key], datetime):
                format_data[key] = int(format_data[key].timestamp())  # 转为时间戳
        return format_data

    async def result_to_async_dict(self, **data):
        """
        一些需要异步处理才能得到的属性，需要等待异步完成，才可以得到结果。
        """
        rv = {key: value for key, value in data.items()}
        for field in self.property_fields:
            property = getattr(self, field)
            if inspect.iscoroutine(property):
                rv[field] = await property
            else:
                rv[field] = property
        return rv

    @classmethod
    async def async_filter(cls, is_get_total_count=False, *args, **kwargs):
        """
        根据条件查询获取, 如果数据不存在，返回空列表;支持分页，支持排序
        :return:  model class列表 or []
        """
        table = cls.__table__
        filters = []
        limit = kwargs.pop('limit', '')
        offset = kwargs.pop('offset', '')
        order_by = kwargs.pop('order_by', 'created_at')
        descending = kwargs.pop('desc', False)
        for key, val in kwargs.items():
            filters.append(getattr(table.c, key) == val)
        async with AsyncSession(DB_Engine) as session:
            query = select(cls).where(and_(*filters)) if len(filters) > 1 else select(cls).where(*filters)
            if is_get_total_count:
                inspector = inspect(cls)  # inspector.primary_key[0]：主键，inspector.primary_key[0].name：主键名
                query_count = select(func.count(inspector.primary_key[0])).where(and_(*filters)) if len(filters) > 1 \
                    else select(func.count(inspector.primary_key[0])).where(*filters)
                total_count_coroutine = await session.execute(query_count)
                total_count = total_count_coroutine.scalar()
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            if order_by:
                query = query.order_by(order_by) if not descending \
                    else query.order_by(desc(order_by))
            res = await session.execute(query)
            res = res.fetchall()
        # 以ORM方式查询返回的结果是一个tuple组成的数组：[(object1, object2)]
        # 当前只有一个model的查询，所以直接取元组的第一个元素
        res = [r[0] for r in res]
        return (res, total_count) if is_get_total_count else res

    @classmethod
    async def async_first(cls, **kwargs):
        """
        根据条件查询获取第一条数据，如果数据不存在，返回空字典
        :return:  model class or {}
        """
        table = cls.__table__
        filters = []
        for key, val in kwargs.items():
            filters.append(getattr(table.c, key) == val)
        async with AsyncSession(DB_Engine) as session:
            if len(filters) > 1:
                query = select(cls).where(and_(*filters))
            else:
                query = select(cls).where(*filters)
            res = await session.execute(query)
            res = res.fetchone()
        if not res:
            return {}
        else:
            return res[0]

    @classmethod
    async def async_in(cls, col, values=[]):
        """
        根据指定字段使用in关键字查询结果.
        :param col: 指定的字段名称
        :param values: in 方法指定的范围
        :return: model class列表或者[]
        """
        table = cls.__table__
        col_schema = getattr(table.c, col)
        in_func = getattr(col_schema, 'in_')
        query = select(cls).where(in_func(values))
        async with AsyncSession(DB_Engine) as session:
            res = await session.execute(query)
            res = res.fetchall()
        res = [r[0] for r in res]
        return res

    async def async_create(self):
        """
        orm model插入db
        """
        async with AsyncSession(DB_Engine, expire_on_commit=False) as session:
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def async_update(cls, *args, **kwargs):
        """
        使用`AsyncEngine`方式更新数据
        :param kwargs: 必须要包含uuid
        :return: 更新的数据记录个数
        """
        table = cls.__table__
        uuid = kwargs.pop('uuid')
        async with DB_Engine.connect() as conn:
            query = table.update(). \
                where(table.c.uuid == uuid). \
                values(**kwargs)
            rv = await conn.execute(query, kwargs)
            await conn.commit()
        return rv.rowcount

    @classmethod
    async def async_delete(cls, **kwargs):
        """
        根据参数过滤结果集，并删除
        :param kwargs: 过滤条件
        :return: 删除的数据记录个数
        """
        table = cls.__table__
        filters = []
        for key, val in kwargs.items():
            filters.append(getattr(table.c, key) == val)
        async with DB_Engine.connect() as conn:
            if len(filters) > 1:
                query = table.delete().where(and_(*filters))
            else:
                query = table.delete().where(*filters)
            rv = await conn.execute(query, kwargs)
            await conn.commit()
        return rv.rowcount


if __name__ == '__main__':
    from myapp.models.desktop import Desktop

    async def filter_desktops():
        dict = {'uuid': '11', 'vm_uuid': '11', 'display_name': '11', 'is_attached_gpu': False, 'is_default': False,
                'enabled': 'enabled', 'node_uuid': '11', 'node_name': '11', 'desc': '11'}
        d = Desktop()
        d.uuid = "11"
        d.vm_uuid = "11"
        d.display_name = "11"
        d.node_uuid = "11"
        d.node_name = "11"

        d = await d.async_create()
        print(d.to_dict())
        # d = await Desktop.async_delete(uuid="11")
        # d = await Desktop.async_save(uuid="11", node_name="xxx")
        # ds = await Desktop.async_filter(uuid="11")
        # ds = await Desktop.async_delete(uuid="12")
        # await Desktop.async_delete(uuid='11')
    loops = asyncio.get_event_loop()
    loops.run_until_complete(asyncio.wait([filter_desktops()]))
