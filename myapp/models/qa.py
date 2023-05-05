from sqlalchemy import Boolean, Column, Enum, String
from myapp.base.db import BaseModel


class Qa(BaseModel):
    __tablename__ = "qa"

    uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="QA的uuid")
    title = Column("title", String(255), nullable=False, comment="QA的标题")
    is_default = Column("is_default", Boolean(), default=False, nullable=False, comment="是否是默认，False表示不是，True表示是。默认False。")
    enabled = Column("enabled", Enum('enabled', 'disabled'), default="enabled", nullable=False, comment="QA的启用状态，enabled表示启用，disabled表示已禁用")

    desc = Column("desc", String(255), default="", nullable=False, comment="QA的描述信息")
