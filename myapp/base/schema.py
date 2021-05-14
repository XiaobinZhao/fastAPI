from enum import Enum
from typing import Generic, TypeVar
from pydantic import validator
from pydantic import Field
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass
from myapp.base.utils import get_base_classes_recursive

ResponseData = TypeVar('ResponseData')


class MyBaseSchema(GenericModel, Generic[ResponseData]):
    """
    统一response返回值。所有对外的API都包含data/message/code/is_success 4个字段。
    :data作为成功返回时的数据内容。
    :message一般在业务失败时返回，进行一定的错误说明。
    :code为业务返回码，成功和失败都有返回码。比如一个API接受参数进行处理，失败的情况可能是参数不合法，
    数据不存在，不允许操作等，成功的情况也可能是业务成功无数据变更，也可能是变更某些数据，业务依然成功，
    每一种情况都可以对应一个code。code可以对应做国际化，亦可以作为规范的用户手册和运维手册来支持用户自服务查询。
    :is_success是业务处理的结果。因为http code不能反馈出一些复杂情况，比如：在当前环境中，有网关，有api服务。
    API的请求在网关处找不到正确路由和在API服务发现需要的资源不存在是不一样的，但是http code 都是404.所以http请求
    本身和业务处理的结果需要分开来表示。
    http code可以用来表示当前请求在业务之前的状态，比如是否在网关处正常（404/504/500等），200只是表示API服务正确的被接受了，
    不代表业务成功。
    当然API服务的处理可能也不能绝对能表达成功和失败的概念，比如，一个异步支付的订单，is_success=1代表前端给的参数都正确，
    后端正确接受了支付申请，不代表支付成功.是否支持成功依然需要去查询订单的状态，比如在is_success=1的情况下再去解析当前
    订单response data中的内容，拿取客户端需要的信息，data里可以是{"orderStatus":"PROCESSING", "orderId":"1234"}，
    这个才是真正业务逻辑的数据和状态。所以是几个层次的事情：Http Status->ApiResult.status->ApiResult.data.orderStatus
    """

    data: ResponseData = Field(default={}, description="response数据包含在这个字段，数据可能是list或者dict.")
    message: str = Field(default="", description="如果有错误发生时，该字段用来显示错误详情。没有错误发生时，字段为空字符串")
    code: str = Field(default=9999, description="请求返回码。默认是9999，代表正常的成功，每个失败都有具体code值。"
                                                "code由几部分组成，具体查看code代码文档")
    is_success: int = Field(default=1, description="api业务处理结果，1代表业务成功，0代表业务失败。")

    @validator('data')
    def format_data(cls, value):
        if value is None:
            value = {}
        return value


class EnabledEnum(str, Enum):
    enabled = "enabled"
    disabled = "disabled"


def get_orm_model_recursive(current_attrs, current_bases):
    """
    递归获取schema model的Config.orm_model字段。该字段一定要在schema中设置才可以融合db model的描述字段。
    Config.orm_model是自定义添加的，不是pydantic设置
    :param current_attrs: 当前class的attrs
    :param current_bases: 当前class的基类列表
    :return: Config.orm_model指向的class。如果找不到该class，抛出一异常。
    """
    if current_attrs.get("Config"):
        return current_attrs.get("Config").orm_model
    bases = get_base_classes_recursive(current_bases[0], [current_bases[0]])
    for base in bases:
        if getattr(base, "Config"):
            return base.Config.orm_model
    raise Exception("Schema model must set Config.orm_model attribute.")


class SchemaMetaclass(ModelMetaclass):
    """
    使用metaclass来改写Schema model class的创建.目的是能够把db model的文档相关字段加入到schema的描述中。
    """
    def __new__(cls, name, bases, attrs):
        """
        通过修改当前class的attrs，主要修改了每个字段属性的description字段，达到可以直接公用db model的描述字段。
        :param name: 当前class的name
        :param bases: 当前class的基类列表
        :param attrs: 当前class的属性
        """
        schema_attrs = attrs["__annotations__"]
        model_attrs = get_orm_model_recursive(attrs, bases)
        for key in schema_attrs:
            model_attr = getattr(model_attrs, key)
            schema_attr_field = attrs.get(key)
            if schema_attr_field.description:
                description = schema_attr_field.description + "<br/>" + model_attr.property.columns[0].comment
            else:
                description = model_attr.property.columns[0].comment
            setattr(schema_attr_field, "description", description)
        return ModelMetaclass.__new__(cls, name, bases, attrs)


def optional_but_cant_empty(cls, values):
    """
    schema reuse validators。限制更新字段可以可选，但是不能全部都不选。
    :param cls: schema model
    :param values: request 传入的参数字典
    :return: 检验失败，raise assertion_error;成功则返回入参字典
    """
    unexpected_fields = set(values.keys()) - set(cls.__fields__)
    assert not bool(unexpected_fields), f'unexpected fields: {unexpected_fields} '
    return values
