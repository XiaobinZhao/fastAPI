from sqlalchemy import Boolean, Column, Enum, String
from myapp.base.db import BaseModel


class Desktop(BaseModel):
    """
    云桌面
    """
    __tablename__ = "desktop"

    uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="自定义桌面uuid")
    vm_uuid = Column("vm_uuid", String(64), index=True, unique=True, default="", nullable=False, comment="虚拟化平台上虚机的uuid")
    display_name = Column("display_name", String(255), nullable=False, comment="桌面的显示名称")
    is_attached_gpu = Column("is_attached_gpu", Boolean(), default=False, nullable=False, comment="桌面是否挂载gpu")
    is_default = Column("is_default", Boolean(), default=False, nullable=False,
                        comment="是否是默认桌面，False表示不是，True表示是。默认False。")
    enabled = Column("enabled", Enum('enabled', 'disabled'), default="enabled", nullable=False,
                     comment="桌面的启用状态，enabled表示启用，disabled表示桌面已禁用")
    node_uuid = Column("node_uuid", String(64), default="", nullable=False, comment="物理机uuid")
    node_name = Column("node_name", String(255), default="", nullable=False, comment="物理机名称")
    desc = Column("desc", String(255), default="", nullable=False, comment="桌面的描述信息")
