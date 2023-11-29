import inspect
from datetime import datetime

from loguru import logger
from sqlalchemy import Column, and_, or_, desc, func
from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import inspect as sql_inspect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import as_declarative, declared_attr

from myapp.conf.config import settings

IGNORE_ATTRS = ["redis"]
DB_Engine = create_async_engine(settings.db.asyncmy,
                                echo=False,
                                pool_size=5,  # 池最大连接数
                                max_overflow=10,  # 池最多溢出连接数
                                pool_recycle=600,  # 池回收connection的间隔，默认不回收（-1）。当前为10分钟。
                                pool_timeout=5)


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
    SQLAlchemy 1.4 support asynchronous.io, 2.0版本转正。建议使用2.0以上版本

    - 查询时，建议使用ORM命名空间的Session和AsyncSession,并且使用scalars()方法去执行fetchall/fetchone等，而不使用Core命名空间的
    Engine,因为Session.execute()返回的是ChunkedIteratorResult，而Engine.connect().execute()返回的是CursorResult。
    ChunkedIteratorResult能够把结果转为对象，而CursorResult不行，类似于：
`   <sqlalchemy.engine.result.ChunkedIteratorResult> [<myapp.models.user.User object at 0x7fa9a47f5210>]
    <sqlalchemy.engine.cursor.CursorResult> ('823cf15b159d4b51912ce15edd53bca2', 'ssss', ...)
    - 其他的修改、删除可以使用engine，也可以使用session
    - 创建，建议使用session，可以直接add/add_all，注意expire_on_commit=false参数的使用，可以在session scope之外访问对象竖向

    SQLAlchemy的ORM继承，在 `classmethod` 和 `staticmethod` 继承是和Python OOP面向对象的继承方案一致的。
    也就是说：
    被冠之`@staticmethod`的静态方法，会被继承，但是在子类调用的时候，却是调用的父类同名方法。
    被冠之`@classmethod`的类方法，会被继承，子类调用的时候就是调用子类的这个方法。
    """

    # Sqlalchemy的抽象方法的定义，代表BaseModel含有抽象方法，需要被子类继承实现；
    # 另外，抽象方法不需要写__tablename__属性
    __abstract__ = True

    created_at = Column("created_at", TIMESTAMP(fsp=3), default=datetime.now, nullable=True, comment="创建时间")
    updated_at = Column("updated_at", TIMESTAMP(fsp=3), default=datetime.now, nullable=True, onupdate=datetime.now,
                        comment="最后修改时间")

    def __init__(self, is_auto_delete_extra_param=True, **kwargs):
        # is_auto_delete_extra_param为True时，遍历传参字段，只获取表中包含字段，去除表中不包含的额外传参。
        if is_auto_delete_extra_param:
            _kwargs = {}
            for field in kwargs:
                if hasattr(self, field):
                    _kwargs[field] = kwargs[field]
            kwargs = _kwargs

        super().__init__(**kwargs)

    def to_dict(self, except_keys=()):
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
                format_data[key] = float(format_data[key].timestamp())
        return format_data

    async def result_to_async_dict(self, **data):
        """
        一些需要异步处理才能得到的属性，需要等待异步完成，才可以得到结果。
        """
        rv = {key: value for key, value in data.items()}
        for field in self.property_fields:
            _property = getattr(self, field)
            if inspect.iscoroutine(_property):
                rv[field] = await _property
            else:
                rv[field] = _property
        return rv

    @classmethod
    async def async_filter(cls, is_get_total_count=False, is_allow_param_empty=False, *args, **kwargs):
        """
        根据条件查询获取, 如果数据不存在，返回空列表;支持分页，支持排序
        :return:  model class列表 or []
        """
        table = cls.__table__
        equal_filter = []
        limit = kwargs.pop("limit", "")
        offset = kwargs.pop("offset", "")
        order_by = kwargs.pop("order_by", "created_at")
        is_desc_sort = kwargs.pop("desc", True)
        or_filter = kwargs.pop("or_filter", {})
        search_key = kwargs.pop("search_key", "")
        not_equal_filter = kwargs.pop("not_equal_filter", {})
        search_str = kwargs.pop("search_str", "")
        start_at = kwargs.pop("start_at", None)
        end_at = kwargs.pop("end_at", None)

        # 已经参与过过滤的key数组
        filter_keys = []
        # 根据字段search_key模糊查询 可匹配多个key,用","隔开
        fuzzy_search_keys = search_key.split(",")
        search_filters = []

        # 模糊查询
        if search_str:
            for key in fuzzy_search_keys:
                if key in table.c:
                    search_filters.append(getattr(table.c, key).like(f"%{search_str}%"))
                    filter_keys.append(key)

        if or_filter:
            for key in or_filter:
                if key not in filter_keys and key in table.c:
                    search_filters.append(getattr(table.c, key) == or_filter[key])
                    filter_keys.append(key)

        if not_equal_filter:
            for key in not_equal_filter:
                if key not in filter_keys and key in table.c:
                    equal_filter.append(getattr(table.c, key) != not_equal_filter[key])
                    filter_keys.append(key)

        for key, val in kwargs.items():
            if key not in filter_keys and key in table.c:
                if val is None:
                    logger.warning("DB query param: %s is None.Ignore." % key)
                    continue
                if val == "":
                    if is_allow_param_empty:
                        equal_filter.append(getattr(table.c, key) == val)
                if isinstance(val, list):
                    equal_filter.append(getattr(table.c, key).in_(val))
                else:
                    equal_filter.append(getattr(table.c, key) == val)
        if start_at:
            equal_filter.append(table.c.created_at >= datetime.fromtimestamp(int(start_at)))
        if end_at:
            equal_filter.append(table.c.created_at <= datetime.fromtimestamp(int(end_at)))
        async with AsyncSession(DB_Engine) as session:
            # 以下设置为[True]是为了兼容SQLAlchemy2.0的语法
            if not equal_filter:
                equal_filter = [True]
            if not search_filters:
                search_filters = [True]
            query = select(cls).where(and_(*equal_filter), or_(*search_filters))

            if is_get_total_count:
                inspector = sql_inspect(cls)  # inspector.primary_key[0]：主键，inspector.primary_key[0].name：主键名
                query_count = select(func.count(inspector.primary_key[0])).where(and_(*equal_filter),
                                                                                 or_(*search_filters))
                total_count_coroutine = await session.execute(query_count)
                total_count = total_count_coroutine.scalar()
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            if order_by:
                query = query.order_by(order_by) if not is_desc_sort \
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
            if hasattr(table.c, key):
                filters.append(getattr(table.c, key) == val)
        async with AsyncSession(DB_Engine) as session:
            query = select(cls).where(and_(*filters))
            res = await session.execute(query)
            # 建议使用scalars的返回值ScalarResult，ScalarResult返回值直接是对象，而不是tuple
            res = res.scalars().one_or_none()

        if not res:
            return
        else:
            return res

    @classmethod
    async def async_in(cls, col, values=()):
        """
        根据指定字段使用in关键字查询结果.
        :param col: 指定的字段名称
        :param values: in 方法指定的范围
        :return: model class列表或者[]
        """
        table = cls.__table__
        col_schema = getattr(table.c, col)
        in_func = getattr(col_schema, "in_")
        query = select(cls).where(in_func(values))
        async with AsyncSession(DB_Engine) as session:
            res = await session.execute(query)
            # 建议使用scalars的返回值ScalarResult，ScalarResult返回值直接是对象，而不是tuple
            res = res.scalars().fetchall()
        return res

    async def async_create(self):
        """
        orm model插入db
        https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#commit-as-you-go
        expire_on_commit=False可以在commit之后，依然可以访问ORM对象属性； 目的是为了能返回self时，可以继续访问self的属性
        """
        async with AsyncSession(DB_Engine, expire_on_commit=False) as session:
            session.add(self)
            await session.commit()
        return self

    @classmethod
    async def async_batch_create(cls, objs=()):
        """
        orm model批量插入db
        https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#begin-once
        使用session和engin 的效果是一样的，可以参看
        https://docs.sqlalchemy.org/en/20/orm/session_transaction.html#session-level-vs-engine-level-transaction-control
        session是SQLAlchemy ORM命名空间下；engin是Core命名空间
        """
        async with AsyncSession(DB_Engine, expire_on_commit=True) as session:
            session.add_all(objs)
            await session.commit()

    @classmethod
    async def async_update_by_uuid(cls, uuid, **kwargs):
        """
        使用`AsyncEngine`方式更新数据
        :param uuid: uuid
        :param kwargs: 必须要包含uuid
        :return: 更新的数据记录个数
        """
        table = cls.__table__
        async with DB_Engine.connect() as conn:
            query = table.update().where(table.c.uuid == uuid).values(**kwargs)
            rv = await conn.execute(query, kwargs)
            await conn.commit()
        return rv.rowcount

    @classmethod
    async def async_update_by_filters(cls, filters: dict, **kwargs):
        """
        使用`AsyncEngine`方式多条件查询更新数据
        :param filters: 多个查询条件
        :param kwargs: 更新的value
        :return: 更新的数据记录个数
        """
        table = cls.__table__
        _filters = []
        for key, val in filters.items():
            if hasattr(table.c, key):
                if isinstance(getattr(table.c, key), list):
                    _filters.append(getattr(table.c, key).in_(val))
                else:
                    _filters.append(getattr(table.c, key) == val)
        async with DB_Engine.connect() as conn:
            query = table.update().where(and_(*_filters)).values(**kwargs)
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
            if hasattr(table.c, key):
                filters.append(getattr(table.c, key) == val)
        async with DB_Engine.connect() as conn:
            query = table.delete().where(and_(*filters))
            rv = await conn.execute(query, kwargs)
            await conn.commit()
        return rv.rowcount

    @classmethod
    async def async_batch_delete(cls, col, values=()):
        """
        orm model批量删除db
        :param col: 指定的字段名称
        :param values: col对应的要删除的字符集
        """
        table = cls.__table__
        filters = []
        for val in values:
            filters.append(getattr(table.c, col) == val)
        if not filters:
            return
        async with DB_Engine.connect() as conn:
            query = table.delete().where(or_(*filters))
            rv = await conn.execute(query)
            await conn.commit()
        return rv.rowcount


if __name__ == '__main__':
    import asyncio
    from myapp.models.user import User

    #
    # async def filter_users():
    #     # dict = {"account": "11", "phone": "11111111111", "desc": "11", "password": "password"}
    #     u = User()
    #     u.uuid = "11"
    #     u.account = "11"
    #     u.phone = "11111111111"
    #     u.password = "password"
    #     u.desc = "11"
    #     u.display_name = "11"
    #     u.user_type = "super_admin"
    #     u.creator_uuid = ""
    #
    #     d = await u.async_create()
    #     print(d.to_dict())
    #     print(await u.async_delete(uuid="11"))
    #     # d = await Desktop.async_delete(uuid="11")
    #     # d = await Desktop.async_save(uuid="11", node_name="xxx")
    #     # ds = await Desktop.async_filter(uuid="11")
    #     # ds = await Desktop.async_delete(uuid="12")
    #     # await Desktop.async_delete(uuid='11')
    #
    # loops = asyncio.get_event_loop()
    # loops.run_until_complete(asyncio.wait([filter_users()]))


    def run_queries(session):
        result = session.execute(select(User).order_by(User.uuid))
        print(type(result))
        for a1 in result.scalars():
            print(a1)
        # query = select(User).where(User.uuid == "823cf15b159d4b51912ce15edd53bca2")
        # # scalarResult写法
        # result = session.execute(query)
        # print(result)
        # a2 = result.scalars().fetchall()
        # print(a2)
        # # Result写法
        # query = select(User).where(User.uuid == "xxx")
        # result = session.execute(query)
        # a3 = result.scalars().one_or_none()
        # print(a3)


    async def async_main():
        async with DB_Engine.begin() as conn:
            stmt = select(User).order_by(User.uuid)
            result = await conn.execute(stmt)
            print(result)
            result2 = result.fetchall()
            print(result2)
            print(type(result2))
            print(type(result2[0]))

            # async_result = await conn.stream(stmt)
            # async for row in async_result:
            #     print(row)
            # result3 = await async_result.all()
            # result4 = await async_result.fetchall()
            # result5 = await async_result.scalars().fetchall()
            # print(result3)
            # print(result4)
            # print(result5)
        async with AsyncSession(DB_Engine) as session:
            query = select(User).order_by(User.uuid)
            res = await session.execute(query)
            # res = res.fetchall()
            # print(res)
            # print(type(res))
            # print(type(res[0]))
            res = res.scalars().fetchall()
            print(res)
            print(type(res))
            print(type(res[0]))

        async with AsyncSession(DB_Engine) as session:
            await session.run_sync(run_queries)
            await session.commit()


    asyncio.run(async_main())
