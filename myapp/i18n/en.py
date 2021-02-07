
class CodeTranslate:

    API_200_000_9999: "success"
    API_500_000_0000: "internal error"
    API_422_000_0001: "request validation error，please check your parameters"
    API_404_000_0002: "the request resource not exist"
    API_401_000_0003: "authentication failed, please check your login_name/password or token"
    API_409_002_0100: "the user login name cannot be duplicated"

    @staticmethod
    def dict():
        return vars(CodeTranslate)["__annotations__"]
