import uvicorn
from loguru import logger
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


logger.configure(**log_configs)  # 配置loguru logger

app = FastAPI(docs_url=None, redoc_url=None)  # docs url 重新定义
custom_openapi(app)  # 设置自定义openAPI


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    拦截所有的exception，返回的数据格式统一为 myapp.base.schema.ResponseModel
    """
    return MyBaseResponse(code=getattr(exc, "code", ErrorCode.FAST_API_ERROR),  # 默认0000为fastAPI系统错误code
                          message=getattr(exc, "message", "") or str(exc.detail),
                          data=getattr(exc, "data", {}),
                          status_code=exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return MyBaseResponse(code=getattr(exc, "code", ErrorCode.FAST_API_ERROR),  # 默认0000为fastAPI系统错误code
                          message=getattr(exc, "message", "") or str(exc),
                          data=getattr(exc, "data", {}),
                          status_code=400)


app.mount("/static", StaticFiles(directory="myapp/static"), name="static")
app.include_router(desktop.router)


if __name__ == '__main__':
    uvicorn.run(app='myapp.main:app',
                host=settings.default.host,
                port=settings.default.port,
                reload=True,
                workers=1)
