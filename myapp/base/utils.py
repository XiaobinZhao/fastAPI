
def get_base_classes_recursive(specified_class, base_class_result=[], stop_name="object"):
    """
    递归查找指定class的基类，直到遇到预设的class name(默认object)
    :param specified_class: 指定的class
    :param stop_name: 预设的停止递归的class name
    :param base_class_result: 返回的最后结果
    :return: List<object> 指定class的基类的列表
    """
    base_classes = specified_class.__bases__
    for base in base_classes:
        base_name = base.__name__
        if base_name != stop_name:
            base_class_result.append(base)
        elif base_name == "object":
            base_class_result.append(object)
            return base_class_result
    return get_base_classes_recursive(base, base_class_result, stop_name)