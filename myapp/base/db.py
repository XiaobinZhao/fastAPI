from json import loads as json_loads
from datetime import datetime
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy import TIMESTAMP, Column
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
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
                          pool_timeout=15,  # 从池获取connection的最长等待时间，默认30s,当前 15s
                          json_serializer=json_serializer,
                          poolclass=QueuePool)  # 默认是QueuePool
SessionFactory = sessionmaker(DB_Engine)


def get_db_data_immediately(model_instance, db_session_result):
    """
    sqlachemy的查询结果是一个session对象，不是我们期望的model对象，所以这里直接把session对象的数据拿出来，转为model对象。
    核心方法其实是把当前的session对象的value set 到当前model对象
    :param model_instance: model 对象实例
    :param db_session_result: sqlachemy的查询结果是一个session对象
    :return: model 对象实例（s）
    """
    def _from_db(obj):
        if not isinstance(obj, Model_Base):  # 如果不是DB model实例，直接返回
            return obj
        new_instance = model_instance.__class__()  # 重新得到一个实例
        for key in model_instance.keys():
            if key in model_instance:
                setattr(new_instance, key, getattr(obj, key))

        return new_instance

    def _from_tuple_db(obj_tuple):
        new_objs = [_from_db(obj) for obj in obj_tuple]
        return tuple(new_objs)

    if not db_session_result:
        return db_session_result

    if isinstance(db_session_result, list):
        model_instances = []
        for db_object in db_session_result:
            if isinstance(db_object, tuple):
                model_instances.append(_from_tuple_db(db_object))
            else:
                model_instances.append(_from_db(db_object))
        return model_instances
    else:
        return _from_db(db_session_result)


def db_session_writer(func):
    @wraps(func)
    def wrap(self, *args, **keywords):
        try:
            self.session = SessionFactory()
            db_session_result = func(self, *args, **keywords)
            self.session.commit()
            result = get_db_data_immediately(self, db_session_result)
            return result
        except SQLAlchemyError:
            self.session.rollback()
            raise
        finally:
            self.session.close()
            self.session = None
    return wrap


def db_session_reader(func):
    @wraps(func)
    def wrap(self, *args, **keywords):
        try:
            self.session = SessionFactory()
            db_session_result = func(self, *args, **keywords)
            result = get_db_data_immediately(self, db_session_result)
            return result
        finally:
            self.session.rollback()  # read 操作不应该对数据库有任何修改操作，否则 rollback
            self.session.close()
            self.session = None
    return wrap


class TimestampMixin(object):
    created_at = Column("created_at", TIMESTAMP(), default=datetime.now, nullable=True, comment="创建时间")
    updated_at = Column("updated_at", TIMESTAMP(), default=datetime.now, nullable=True, onupdate=datetime.now,
                        comment="最后修改时间")


class ModelIterator(object):

    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    def __next__(self):
        n = next(self.i)
        return n, getattr(self.model, n)


class ModelDB(object):
    def __init__(self):
        self.session = None

    def _get_columns(self):
        return [prop.key for prop in self.__mapper__.iterate_properties]

    @db_session_writer
    def add(self):
        self.session.add(self)
        return self

    @db_session_writer
    def delete(self):
        self.session.query(self.__class__).filter_by(uuid=self.uuid).delete()

    @db_session_reader
    def get_by_id(self):
        return self.session.query(self.__class__).filter_by(uuid=self.uuid).first()

    @db_session_reader
    def get_all(self):
        return self.session.query(self.__class__).all()

    @db_session_reader
    def get_by_page(self, skip: int, limit: int):
        return self.session.query(self.__class__).offset(skip).limit(limit).all()

    @db_session_writer
    def update(self):
        new_dict = self._as_dict(except_keys=["id", "uuid", "created_at", "updated_at"])
        result = self.session.query(self.__class__).filter_by(uuid=self.uuid).update(new_dict)
        return result

    def _as_dict(self, except_keys=[]):
        """Make the model object behave like a dict.
           Includes attributes from joins.
           :param list <except_keys>: 不期望返回的字段
        """
        local = dict((key, value) for key, value in self if key not in except_keys)  # 需要实现__iter__
        # joined = dict([(k, v) for k, v in self.__dict__.items()
        #               if not k[0] == '_'])
        # local.update(joined)
        return local

    def iteritems(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def items(self):
        """Make the model object behave like a dict."""
        return self._as_dict().items()

    def keys(self):
        """Make the model object behave like a dict."""
        return [key for key, value in self.iteritems()]

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __contains__(self, key):
        # Don't use hasattr() because hasattr() catches any exception, not only
        # AttributeError. We want to passthrough SQLAlchemy exceptions
        # (ex: sqlalchemy.orm.exc.DetachedInstanceError).
        try:
            getattr(self, key)
        except AttributeError:
            return False
        else:
            return True

    def __iter__(self):
        columns = [prop.key for prop in self.__mapper__.iterate_properties]
        return ModelIterator(self, iter(columns))
