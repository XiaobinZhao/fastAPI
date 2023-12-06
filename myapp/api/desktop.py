from typing import List
from fastapi import status, Query
from fastapi import Depends

from myapp.base.context import request_context
from myapp.manager.log import log

from myapp.base.schema import MyBaseSchema, PageSchema, MyFilterQueryParam
from myapp.base.router import MyRouter
from myapp.schema.desktop import DesktopBase as DesktopBaseSchema
from myapp.schema.desktop import DesktopDetail as DesktopDetailSchema
from myapp.schema.desktop import DesktopPatch as DesktopPatchSchema
from myapp.manager.desktop import DesktopManager
from myapp.manager.token import verify_token
from myapp.models.desktop import Desktop as DB_Desktop_Model

router = MyRouter(prefix="/desktops", tags=["desktop"], dependencies=[Depends(verify_token)],
                  responses={status.HTTP_401_UNAUTHORIZED: {"model": MyBaseSchema}})


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"model": MyBaseSchema[DesktopDetailSchema]}})
@log("desktop", "create", operation_desc="创建桌面")
async def create_desktop(desktop: DesktopBaseSchema):
    manager = DesktopManager()
    desktop: DB_Desktop_Model = await manager.create_desktop(desktop)
    request_context.update({"obj_id": desktop.uuid, "obj_name": desktop.display_name})
    return MyBaseSchema[DesktopDetailSchema](data=desktop)


@router.get("/", response_model=MyBaseSchema[List[DesktopDetailSchema]])
async def list_desktops(search_key: str = "display_name", search_str: str = "",
                        filters: MyFilterQueryParam = Query(default={},
                                                            description="其他过滤条件，必须符合a=xx,b=xx的键值对格式")):
    """
    查询桌面列表.
    """
    manager = DesktopManager()
    desktops = await manager.list_desktops(search_key=search_key, search_str=search_str, filters=filters)
    return MyBaseSchema[List[DesktopDetailSchema]](data=desktops)


@router.get("/page", response_model=MyBaseSchema[PageSchema[List[DesktopDetailSchema]]])
async def page_desktops(search_key: str = "display_name", search_str: str = "",
                        filters: MyFilterQueryParam = Query(default={}, description="其他过滤条件，必须符合a=xx,b=xx的键值对格式"),
                        skip: int = 0, limit: int = 100):
    """
    查询桌面列表.
    """
    manager = DesktopManager()
    page_data = await manager.page_desktops(search_key=search_key, search_str=search_str, filters=filters,
                                            skip=skip, limit=limit)
    return MyBaseSchema[PageSchema[List[DesktopDetailSchema]]](data=page_data)


@router.get("/{desktop_uuid}", response_model=MyBaseSchema[DesktopDetailSchema])
async def get_desktop_detail(desktop_uuid: str):
    """
    指定UUID查询桌面详情.
    """
    manager = DesktopManager()
    desktop = await manager.get_desktop_by_uuid(desktop_uuid)
    return MyBaseSchema[DesktopDetailSchema](data=desktop)


@router.delete("/{desktop_uuid}", response_model=MyBaseSchema)
@log("desktop", "delete", operation_desc="删除桌面")
async def delete_desktop(desktop_uuid: str):
    """
    指定UUID删除桌面.
    """
    request_context.update({"obj_id": desktop_uuid, "obj_name": "desktop_id"})
    manager = DesktopManager()
    await manager.delete_desktop_by_uuid(desktop_uuid)
    return MyBaseSchema(data=None)


@router.patch("/{desktop_uuid}", response_model=MyBaseSchema[DesktopDetailSchema])
@log("desktop", "update", operation_desc="更新桌面")
async def patch_desktop(desktop_uuid: str, desktop: DesktopPatchSchema):
    request_context.update({"obj_id": desktop_uuid})
    manager = DesktopManager()
    desktop: DB_Desktop_Model = await manager.patch_desktop(desktop_uuid, desktop)
    request_context.update({"obj_name": desktop.display_name})
    return MyBaseSchema[DesktopDetailSchema](data=desktop)
