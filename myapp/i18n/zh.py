
class CodeTranslate:

    API_200_000_9999: "成功"
    API_500_000_0000: "未知系统错误"
    API_422_000_0001: "request 请求参数校验失败，请检查参数格式"
    API_404_000_0002: "请求的资源不存在"
    API_401_000_0003: "认证失败"
    API_409_002_0100: "用户登录名不能重复"

    @staticmethod
    def dict():
        return vars(CodeTranslate)["__annotations__"]
