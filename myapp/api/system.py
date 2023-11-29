from myapp.manager.token import Signature
from fastapi import status, Depends
from loguru import logger

from myapp.base.router import MyRouter
from myapp.base.schema import MyBaseSchema
from myapp.manager.system import SystemManager
from myapp.schema.system import LanguageI18n
from myapp.utils.snowflake import IDWorker

router = MyRouter(prefix="/system", tags=["system"], responses={status.HTTP_401_UNAUTHORIZED: {"model": MyBaseSchema}})


@router.get("/id", response_model=MyBaseSchema)
async def snowflake_id():
    return MyBaseSchema(data=IDWorker.gen_id())


@router.get("/i18n", response_model=MyBaseSchema[LanguageI18n], dependencies=[Depends(Signature())])
async def i18n_collection():
    """
    返回系统产生的i18n合集
    """
    manager = SystemManager()
    i18n = await manager.get_i18n_collection()
    return MyBaseSchema[LanguageI18n](data=i18n)


@router.get("/version", response_model=MyBaseSchema, dependencies=[Depends(Signature())])
async def get_version():
    """
    返回系统版本号
    """
    try:
        from myapp.main import root_path
        version_path = root_path.parent.joinpath("version.txt")
        with open(version_path, 'r') as file:
            version = file.read().rstrip()
    except Exception as e:
        logger.error(str(e))
        version = ""
    return MyBaseSchema(data={"version": version})
