from sqlalchemy import Column, Enum, String, Integer, Boolean, TIMESTAMP
from myapp.base.db import BaseModel
from datetime import datetime


class Jjtest(BaseModel):
    """
    jjtest
    """
    __tablename__ = "jjtest"

    uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="uuid")
    login_name = Column("login_name", String(64), unique=True, nullable=False, comment="登录名")
    password = Column("password", String(255), nullable=False, comment="密码")
    display_name = Column("display_name", String(255), index=True, nullable=False, comment="姓名")
    email = Column("email", String(255), nullable=False, comment="邮箱")
    enabled = Column("enabled", Enum('enabled', 'disabled'), default="enabled", nullable=False,
                     comment="用户的启用状态，enabled表示启用，disabled表示禁用")
    desc = Column("desc", String(255), default="", nullable=False, comment="描述信息")
    age = Column("age", Integer, nullable=False, comment="age")
    sex = Column('sex', Boolean, nullable=False, comment="是否为男")
    time = Column('time', TIMESTAMP(), default=datetime.now(), nullable=False, comment="时间")
