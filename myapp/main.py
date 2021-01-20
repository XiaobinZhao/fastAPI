import uvicorn
from loguru import logger
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from myapp.openapi import custom_openapi
from myapp.conf.config import settings
from myapp.conf.loginit import config as log_configs
from myapp.api import desktop

logger.configure(**log_configs)  # 配置loguru logger


app = FastAPI(docs_url=None, redoc_url=None)  # docs url 重新定义
custom_openapi(app)  # 设置自定义openAPI

app.mount("/static", StaticFiles(directory="myapp/static"), name="static")
app.include_router(desktop.router)


if __name__ == '__main__':
    uvicorn.run(app='myapp.main:app',
                host=settings.default.host,
                port=settings.default.port,
                reload=True,
                workers=1)
