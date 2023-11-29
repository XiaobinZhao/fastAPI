from typing import List
from fastapi import status, Query
from fastapi import Depends
from myapp.base.schema import MyBaseSchema, PageSchema, MyFilterQueryParam
from myapp.base.router import MyRouter
from myapp.schema.desktop import DesktopBase as DesktopBaseSchema
from myapp.schema.desktop import DesktopDetail as DesktopDetailSchema
from myapp.schema.desktop import DesktopPatch as DesktopPatchSchema
from myapp.manager.desktop import DesktopManager
from myapp.manager.token import verify_token

router = MyRouter(prefix="/desktops", tags=["desktop"], dependencies=[Depends(verify_token)],
                  responses={status.HTTP_401_UNAUTHORIZED: {"model": MyBaseSchema}})


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"model": MyBaseSchema[DesktopDetailSchema]}})
async def create_desktop(desktop: DesktopBaseSchema):
    manager = DesktopManager()
    desktop = await manager.create_desktop(desktop)
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
async def delete_desktop(desktop_uuid: str):
    """
    指定UUID删除桌面.
    """
    manager = DesktopManager()
    desktop = await manager.delete_desktop_by_uuid(desktop_uuid)
    return MyBaseSchema(data=desktop)


@router.patch("/{desktop_uuid}", response_model=MyBaseSchema[DesktopDetailSchema])
async def patch_desktop(desktop_uuid: str, desktop: DesktopPatchSchema):
    manager = DesktopManager()
    desktop = await manager.patch_desktop(desktop_uuid, desktop)
    return MyBaseSchema[DesktopDetailSchema](data=desktop)
