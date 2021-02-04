from sqlalchemy import Column, Enum, String
from myapp.base.db import Model_Base
from myapp.base.db import ModelDB
from myapp.base.db import TimestampMixin


class User(Model_Base, TimestampMixin, ModelDB):
    """
    用户
    """
    __tablename__ = "user"

    uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="uuid")
    login_name = Column("login_name", String(64), unique=True, nullable=False, comment="登录名")
    password = Column("password", String(255), nullable=False, comment="密码")
    display_name = Column("display_name", String(255), index=True, nullable=False, comment="姓名")
    email = Column("email", String(255), nullable=False, comment="邮箱")
    phone = Column("phone", String(255), nullable=False, comment="电话")
    enabled = Column("enabled", Enum('enabled', 'disabled'), default="enabled", nullable=False,
                     comment="用户的启用状态，enabled表示启用，disabled表示禁用")
    desc = Column("desc", String(255), default="", nullable=False, comment="描述信息")
