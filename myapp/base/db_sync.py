from datetime import datetime

from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy import Column, select, delete, update
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from myapp.conf.config import settings

DB_Engine = create_engine(settings.db.pymysql_url,
                          echo=False,
                          pool_size=5,  # 池最大连接数
                          max_overflow=10,  # 池最多溢出连接数
                          pool_recycle=600,  # 池回收connection的间隔，默认不回收（-1）。当前为10分钟。
                          pool_timeout=15,  # 从池获取connection的最长等待时间，默认30s,当前 15s
                          )
Session = sessionmaker(DB_Engine)


class ModelIterator(object):

    def __init__(self, model, columns):
        self.model = model
        self.i = columns

    def __iter__(self):
        return self

    def __next__(self):
        n = next(self.i)
        return n, getattr(self.model, n)


class ModelBase(DeclarativeBase):
    created_at = Column("created_at", TIMESTAMP(fsp=3), default=datetime.now, nullable=True, comment="创建时间")
    updated_at = Column("updated_at", TIMESTAMP(fsp=3), default=datetime.now, nullable=True, onupdate=datetime.now,
                        comment="最后修改时间")


class ModelDB(object):

    def add(self):
        with Session(expire_on_commit=False) as session:  # expire_on_commit=False可以让self model对象属性依然可以访问
            with session.begin():
                session.add(self)
                return self

    @classmethod
    def delete(cls, **kwargs):
        filters = []
        for key, val in kwargs.items():
            if getattr(cls, key, None):
                filters.append(getattr(cls, key) == val)

        with Session() as session:
            query = delete(cls).where(*filters)
            rv = session.execute(query)
            session.commit()
        return rv.rowcount

    @classmethod
    def get_by_id(cls, uuid):
        with Session() as session:
            query = select(cls).where(getattr(cls, "uuid") == uuid)
            return session.execute(query).scalars().one_or_none()

    @classmethod
    def get_by_conditions(cls, **conditions):
        filters = []
        for key, val in conditions.items():
            if getattr(cls, key, None):
                filters.append(getattr(cls, key) == val)

        with Session() as session:
            query = select(cls).where(*filters)
            return session.execute(query).scalars().fetchall()

    @classmethod
    def get_all(cls):
        with Session() as session:
            query = select(cls)
            return session.execute(query).scalars().fetchall()

    @classmethod
    def get_by_page(cls, skip: int, limit: int):
        with Session() as session:
            query = select(cls).offset(skip).limit(limit)
            return session.execute(query).scalars().fetchall()

    @classmethod
    def update(cls, **kwargs):
        uuid = kwargs.pop("uuid")
        with Session(expire_on_commit=False) as session:
            query = update(cls).where(cls.uuid == uuid).values(**kwargs)
            rv = session.execute(query)
            session.commit()
            return rv.rowcount

    def as_dict(self, except_keys=()):
        """
        :param except_keys: 不期望返回的字段
        """
        local = {}
        for key, value in self:  # 需要实现__iter__
            if key in except_keys:
                continue
            elif isinstance(value, datetime):
                value = int(value.timestamp())  # 转为时间戳
            local[key] = value

        return local

    def iteritems(self):
        """Make the model object behave like a dict."""
        return self.as_dict().items()

    def items(self):
        """Make the model object behave like a dict."""
        return self.as_dict().items()

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


if __name__ == '__main__':
    from sqlalchemy import Column, Enum, String, Boolean


    class User(ModelBase, ModelDB):
        __tablename__ = "user"

        uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="uuid")
        account = Column("account", String(64), unique=True, nullable=False, default="", comment="登录账户")
        password = Column("password", String(255), nullable=False, default="", comment="密码")
        phone = Column("phone", String(15), unique=True, nullable=False, default="", comment="电话")
        display_name = Column("display_name", String(255), default="", index=True, nullable=False, comment="姓名")
        company = Column("company", String(255), default="", nullable=False, comment="用户所在企业名称")
        user_type = Column("user_type", Enum("super_admin", "normal_admin", "user"), default="user", nullable=False,
                           comment="用户类型，super_admin表示超管，normal_admin表示普通管理员，user表示用户")
        enabled = Column("enabled", Boolean(), default=True, nullable=False,
                         comment="用户是否可登录，enabled表示可登录，disabled表示禁止", )
        creator_uuid = Column("creator_uuid", String(64), nullable=False, default="", comment="创建人uuid")
        desc = Column("desc", String(255), default="", nullable=False, comment="描述信息")


    u = User()
    u.uuid = "xxxx"
    u.desc = "xxxx"
    new_u = u.add()
    print(new_u.as_dict())

    all_user = User.get_all()
    print(all_user)

    uuid_user = User.get_by_id(u.uuid)
    print(uuid_user)

    page_user = User.get_by_page(0, 1)
    print(page_user)

    conditions_user = User.get_by_conditions(uuid=u.uuid)
    print(conditions_user)

    update_user = u.update(uuid=u.uuid, desc="yyyy")
    print(update_user)

    uuid_user = User.get_by_id(u.uuid)
    print(uuid_user.as_dict())

    delete_count = User.delete(uuid=u.uuid)
    print(delete_count)
