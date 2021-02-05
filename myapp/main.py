import uvicorn
from loguru import logger
from fastapi import status
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from myapp.openapi import custom_openapi
from myapp.conf.config import settings
from myapp.conf.loginit import config as log_configs
from myapp.base.response import MyBaseResponse
from myapp.base.code import ErrorCode
from myapp.api import desktop
from myapp.api import user
from myapp.api import token


logger.configure(**log_configs)  # 配置loguru logger

app = FastAPI(docs_url=None, redoc_url=None)  # docs url 重新定义
custom_openapi(app)  # 设置自定义openAPI


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    拦截所有的exception，返回的数据格式统一为 myapp.base.schema.ResponseModel
    """
    code = ErrorCode().INTERNAL_ERROR  # 默认0000为系统未知错误code
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        code = ErrorCode().UNAUTHORIZED_ERROR
    return MyBaseResponse(code=getattr(exc, "code", code),
                          message=getattr(exc, "message", "") or str(exc.detail),
                          data=getattr(exc, "data", {}),
                          status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return MyBaseResponse(code=getattr(exc, "code", ErrorCode().REQUEST_VALIDATE_ERROR),
                          message=getattr(exc, "message", "") or str(exc),
                          data=getattr(exc, "data", {}),
                          status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


app.mount("/static", StaticFiles(directory="myapp/static"), name="static")
app.include_router(token.router)
app.include_router(desktop.router)
app.include_router(user.router)


if __name__ == '__main__':
    uvicorn.run(app='myapp.main:app',
                host=settings.default.host,
                port=settings.default.port,
                reload=True,
                workers=1)
