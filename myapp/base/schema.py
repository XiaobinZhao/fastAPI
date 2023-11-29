import urllib.parse as urlparse
from datetime import datetime
from typing import Generic, TypeVar, Union

from pydantic import Field
from pydantic import validator
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass

from myapp.base.code import SuccessCode
from myapp.base.utils import get_base_classes_recursive

ResponseData = TypeVar("ResponseData")


class MyBaseSchema(GenericModel, Generic[ResponseData]):
    """
    统一response返回值。所有对外的API都包含data/message/code三个字段
    """

    data: ResponseData = Field(default={}, description="response数据包含在这个字段，数据可能是list或者dict.")
    message: str = Field(default="",
                         description="如果有错误发生时，该字段用来显示错误详情。没有错误发生时，字段为空字符串")
    code: str = Field(default=SuccessCode.SUCCESS()["code"],
                      description="请求返回码。每个失败都有具体code值。code由几部分组成")

    @validator("data")
    def format_data(cls, value):
        if value is None:
            value = {}
        return value


class PageSchema(GenericModel, Generic[ResponseData]):
    """
    分页的返回值
    """

    total: int = Field(default=0, description="共计")
    limit: int = Field(default=10, description="每页值")
    skip: int = Field(default=0, description="偏移量")
    data: ResponseData = Field(default={}, description="response数据包含在这个字段，数据可能是list或者dict.")


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
        if getattr(base, "Config", None) and getattr(base.Config, "orm_model", None):
            return base.Config.orm_model
    return None


class SchemaMetaclass(ModelMetaclass):
    """
    使用metaclass来改写Schema model class的创建.目的是能够把db model的文档相关字段加入到schema的描述中。
    """

    def __new__(mcs, name, bases, attrs):
        """
        通过修改当前class的attrs，主要修改了每个字段属性的description字段，达到可以直接公用db model的描述字段。
        :param name: 当前class的name
        :param bases: 当前class的基类列表
        :param attrs: 当前class的属性
        """
        schema_attrs = attrs["__annotations__"]
        model_attrs = get_orm_model_recursive(attrs, bases)
        if not model_attrs:
            return ModelMetaclass.__new__(mcs, name, bases, attrs)
        for key in schema_attrs:
            if not hasattr(model_attrs, key):
                continue
            model_attr = getattr(model_attrs, key)
            schema_attr_field = attrs.get(key)
            if schema_attr_field.description:
                description = schema_attr_field.description + "<br/>" + model_attr.property.columns[0].comment
            else:
                description = model_attr.property.columns[0].comment
            setattr(schema_attr_field, "description", description)
        return ModelMetaclass.__new__(mcs, name, bases, attrs)


def optional_but_cant_empty(cls, values):
    """
    schema reuse validators。限制更新字段可以可选，但是不能全部都不选。
    :param cls: schema model
    :param values: request 传入的参数字典
    :return: 检验失败，raise assertion_error;成功则返回入参字典
    """
    unexpected_fields = set(values.keys()) - set(cls.__fields__)
    assert not bool(unexpected_fields), f"unexpected fields: {unexpected_fields} "
    return values


class MyTimestamp(int):
    """
    定义 myappTimestamp 时间戳模型字段
    接收各种类型的时间 转换为int类型的 UNIX 时间戳
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Union[str, int, float, datetime]):
        # 转换为 datetime 类型
        if isinstance(v, str):
            v = datetime.strptime(v, "%Y-%m-%d %H:%M:%S.%f")
        elif isinstance(v, (int, float)):
            return float(v)
        elif not isinstance(v, datetime):
            raise TypeError(f'Invalid type for Timestamp: {type(v).__name__}')
        # 返回转换后的 myappTimestamp 对象
        return float(v.timestamp())


class MyFilterQueryParam(str):
    """
    定义 列表查询时的过滤 filters字段； 必须符合空字符串或者逗号分隔的key-value形式，比如
    filters=key1=val,key2=val2
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: str = ""):
        if v == "":
            return {}
        try:
            filters = dict(urlparse.parse_qsl(v, strict_parsing=True, separator=","))  # 转成字典
        except Exception as e:
            raise ValueError("filters must be one or more key-value patten, like: a=xx,b=xx")
        return filters
