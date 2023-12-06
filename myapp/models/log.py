from sqlalchemy import Column, String, Enum, TEXT, BLOB

from myapp.base.db_async import BaseModel


class Log(BaseModel):
    """
    操作日志
    """

    __tablename__ = "log"

    uuid = Column("uuid", String(64), primary_key=True, nullable=False, comment="uuid")
    user_uuid = Column("user_uuid", String(255), default="", nullable=False, comment="产生操作日志所属的用户ID")
    user_email = Column("user_email", String(255), default="", nullable=False, comment="产生操作日志所属的用户email")
    user_type = Column("user_type", String(50), default="user", nullable=False, comment="产生操作日志所属的用户类型admin/user")
    app_type = Column("app_type", String(50), default="web", nullable=False,
                      comment="表示发送的app类型，可以是android/ios/web")
    app_release = Column("app_release", String(50), nullable=False, default="", comment="版本号")
    level = Column("level", String(50), nullable=False, default="1",
                   comment="日志级别,DEBUG: 1, INFO: 2, ALERT: 3, ERROR: 4, FATAL: 5")
    domain = Column("domain", String(50), nullable=False, default="", comment="表示这个log是关于哪个方面问题")
    sub_domain = Column("sub_domain", String(50), nullable=False, default="", comment="表示这个log是哪个细节方面的问题")
    action = Column("action", String(255), default="", nullable=False, comment="具体操作，比如create/update/delete等")
    obj_id = Column("obj_id", String(255), default="", nullable=False, comment="操作对象id")
    obj_name = Column("obj_name", String(255), default="", nullable=False, comment="操作对象name")
    ref_id = Column("ref_id", String(255), default="", nullable=False, comment="涉及相关对象id")
    ref_name = Column("ref_name", String(255), default="", nullable=False, comment="涉及相关对象的name")
    req_id = Column("req_id", String(32), default="", nullable=False, comment="request id")
    status = Column("status", Enum('success', 'fail', 'unknown'), default="unknown", nullable=False, comment="操作的结果")
    request_ip = Column("request_ip", String(20), default="", nullable=False, comment="操作的请求ip")
    error_code = Column("error_code", String(64), default="", nullable=False, comment="操作错误的错误码")
    error_message = Column("error_message", TEXT(), default="", nullable=False, comment="操作错误时记录错误信息")
    extra = Column("extra", TEXT(), default="", nullable=False, comment="一些其他内容或者异常堆栈信息/上下文")
    request_params = Column("request_params", BLOB(), default=b"", nullable=True, comment="操作日志的请求参数")
    response_body = Column("response_body", BLOB(), default=b"", nullable=True, comment="操作对应返回的数据")
    operation_desc = Column("operation_desc", String(1024), default="", nullable=False, comment="可以被理解的描述信息")
