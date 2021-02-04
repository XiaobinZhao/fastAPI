from typing import List
from fastapi import status
from fastapi import Depends
from myapp.base.schema import MyBaseSchema
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
def create_desktop(desktop: DesktopBaseSchema):
    manager = DesktopManager()
    desktop = manager.create_desktop(desktop)
    return MyBaseSchema[DesktopDetailSchema](data=desktop)


@router.get("/", response_model=MyBaseSchema[List[DesktopDetailSchema]])
def list_desktops(skip: int = 0, limit: int = 100):
    """
    查询桌面列表.
    """
    manager = DesktopManager()
    desktops = manager.list_desktops(skip=skip, limit=limit)
    return MyBaseSchema[List[DesktopDetailSchema]](data=desktops)


@router.get("/{desktop_uuid}", response_model=MyBaseSchema[DesktopDetailSchema])
def get_desktop_detail(desktop_uuid: str):
    """
    指定UUID查询桌面详情.
    """
    manager = DesktopManager()
    desktop = manager.get_desktop_by_uuid(desktop_uuid)
    return MyBaseSchema[DesktopDetailSchema](data=desktop)


@router.delete("/{desktop_uuid}", response_model=MyBaseSchema)
def delete_desktop(desktop_uuid: str):
    """
    指定UUID删除桌面.
    """
    manager = DesktopManager()
    desktop = manager.delete_desktop_by_uuid(desktop_uuid)
    return MyBaseSchema(data=desktop)


@router.patch("/{desktop_uuid}", response_model=MyBaseSchema[DesktopDetailSchema])
def patch_desktop(desktop_uuid: str, desktop: DesktopPatchSchema):
    manager = DesktopManager()
    desktop = manager.patch_desktop(desktop_uuid, desktop)
    return MyBaseSchema[DesktopDetailSchema](data=desktop)
