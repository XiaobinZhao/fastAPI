from sqlalchemy import Column, Enum, String
from myapp.base.db import BaseModel


class User(BaseModel):
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
    company = Column("company", String(255), nullable=False, comment="企业")
    enabled = Column("enabled", Enum('enabled', 'disabled'), default="enabled", nullable=False,
                     comment="用户的启用状态，enabled表示启用，disabled表示禁用")
    role = Column("role", Enum('admin', 'user'), default="user", nullable=False,
                     comment="用户的角色，admin表示管理员，user表示普通用户")
    status = Column("status", Enum('black', 'white'), default="white", nullable=False,
                     comment="用户的状态，black表示黑名单，white表示白名单")
    auth_group = Column("auth_group", String(255), default="", nullable=False, comment="分组管理权限")
    auth_qa = Column("auth_qa", String(255), default="", nullable=False, comment="Q@A管理权限")
    auth_admin = Column("auth_admin", String(255), default="", nullable=False, comment="管理员权限")
    auth_user = Column("auth_user", String(255), default="", nullable=False, comment="用户管理权限")
    desc = Column("desc", String(255), default="", nullable=False, comment="描述信息")
