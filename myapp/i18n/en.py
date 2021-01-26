
class CodeTranslate:

    API_9999: "success"
    API_0000: "internal error"
    API_0001: "request validation error，please check your parameters"

    @staticmethod
    def dict():
        return vars(CodeTranslate)["__annotations__"]
