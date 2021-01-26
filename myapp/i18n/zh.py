
class CodeTranslate:

    API_9999: "成功"
    API_0000: "未知系统错误"
    API_0001: "request 请求参数校验失败，请检查参数格式"

    @staticmethod
    def dict():
        return vars(CodeTranslate)["__annotations__"]
