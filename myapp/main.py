import pathlib

import uvicorn
from loguru import logger
from fastapi import status
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from myapp.utils import generate_i18n

from myapp.base.cache import MyCache
from myapp.openapi import custom_openapi
from myapp.conf.config import settings
from myapp.conf.loginit import config as log_configs
from myapp.base.response import MyBaseResponse
from myapp.base.code import ErrorCode
from myapp.error_code.auth import ErrorCode as AuthErrorCode
from myapp.api import desktop
from myapp.api import user
from myapp.api import token
from myapp.api import log
from myapp.api import system


logger.configure(**log_configs)  # 配置loguru logger

root_path = pathlib.Path(__file__).parent.resolve()  # 使用绝对路径，防止环境不同导致的异常

app = FastAPI(docs_url=None, redoc_url=None)  # docs url 重新定义
custom_openapi(app)  # 设置自定义openAPI


@app.on_event('startup')
async def startup_event():
    generate_i18n.main()


@app.on_event('shutdown')
async def shutdown_event():
    await MyCache.close()


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def http_exception_handler(request, exc):
    """
    拦截所有的 500 返回
    """
    code = ErrorCode.INTERNAL_ERROR()["code"]  # 默认0000为系统未知错误code
    message = str(exc.__dict__)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return MyBaseResponse(code=code, message=message, status_code=status_code)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    拦截所有的exception，返回的数据格式统一为 myapp.base.schema.ResponseModel
    """
    code = ErrorCode.INTERNAL_ERROR()["code"]  # 默认0000为系统未知错误code
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:  # 专门拦截OAuth2PasswordBearer的401
        code = AuthErrorCode.UNAUTHORIZED_ERROR()["code"]
    message = getattr(exc, "message", "") or str(exc.__dict__)
    logger.warning(message)
    return MyBaseResponse(code=getattr(exc, "code", code), message=message,
                          data=getattr(exc, "data", {}), status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return MyBaseResponse(code=getattr(exc, "code", ErrorCode.REQUEST_VALIDATE_ERROR()["code"]),
                          message=getattr(exc, "message", "") or str(exc),
                          data=getattr(exc, "data", {}),
                          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


app.mount("/static", StaticFiles(directory=str(root_path.joinpath("static"))))
app.include_router(token.router)
app.include_router(desktop.router)
app.include_router(user.router)
app.include_router(log.router)
app.include_router(system.router)


if __name__ == '__main__':
    uvicorn.run(app='myapp.main:app',
                host=settings.default.host,
                port=settings.default.port,
                reload=True,
                workers=1,
                limit_concurrency=10)
