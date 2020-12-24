import uvicorn
from loguru import logger
from fastapi import FastAPI
from myapp.api import desktop
from myapp.conf.config import settings
from myapp.conf.loginit import config as log_configs

logger.configure(**log_configs)  # 配置loguru logger


tags_metadata = [
    {
        "name": "desktop",
        "description": "Manage desktops. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

app = FastAPI(title="My App",
              description="my app description",
              version="1.0.0",
              openapi_tags=tags_metadata,
              openapi_url="/api/openapi.json")

# app.include_router(desktop.router,
#                    prefix="/desktops",
#                    tags=["desktop"],
#                    dependencies=None,
#                    responses=None,
#                    default_response_class=None)


if __name__ == '__main__':
    uvicorn.run(app='myapp.main:app',
                host=settings.default.host,
                port=settings.default.port,
                reload=True,
                debug=True,
                workers=1)
