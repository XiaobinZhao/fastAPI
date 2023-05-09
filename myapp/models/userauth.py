from sqlalchemy import Column, String
from myapp.base.db import BaseModel


class Userauth(BaseModel):
    """
    用户权限
    """
    __tablename__ = "userauth"

    user_uuid = Column("user_uuid", String(64), primary_key=True, nullable=False, comment="user_uuid")
    group = Column("group", String(255), default="", nullable=False, comment="分组管理权限")
    qa = Column("qa", String(255), default="", nullable=False, comment="Q@A管理权限")
    admin = Column("admin", String(255), default="", nullable=False, comment="管理员权限")
    user = Column("user", String(255), default="", nullable=False, comment="用户管理权限")
