from enum import Enum
from typing import Generic, TypeVar
from pydantic import Field
from pydantic.generics import GenericModel
from pydantic.main import ModelMetaclass
from myapp.base.utils import get_base_classes_recursive

ResponseData = TypeVar('ResponseData')


class MyBaseSchema(GenericModel, Generic[ResponseData]):
    """
    统一response返回值。所有对外的API都包含data/message/code三个字段
    """
    data: ResponseData = Field(default={}, description="response数据包含在这个字段，数据可能是list或者dict.")
    message: str = Field(default="", description="如果有错误发生时，该字段用来显示错误详情。没有错误发生时，字段为空字符串")
    code: str = Field(default=9999, description="请求返回码。成功默认是9999，每个失败都有具体code值。code由几部分组成")


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
