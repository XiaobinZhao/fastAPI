from typing import List
from fastapi import status
from myapp.base.schema import MyBaseSchema
from myapp.schema.desktop import DesktopBase as DesktopBaseSchema
from myapp.schema.desktop import DesktopDetail as DesktopDetailSchema
from myapp.schema.desktop import DesktopPatch as DesktopPatchSchema
from myapp.manager.desktop import DesktopManager
from myapp.base.response import CommonResponse
from myapp.base.router import MyRouter

router = MyRouter(prefix="/desktops", tags=["desktop"])


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"model": MyBaseSchema[DesktopDetailSchema]}})
def create_desktop(desktop: DesktopBaseSchema):
    manager = DesktopManager()
    desktop = manager.create_desktop(desktop)
    return desktop


@router.get("/", responses={status.HTTP_200_OK: {"model": MyBaseSchema[List[DesktopDetailSchema]]}})
def list_desktops(skip: int = 0, limit: int = 100):
    """
    查询桌面列表.
    """
    manager = DesktopManager()
    desktops = manager.list_desktops(skip=skip, limit=limit)
    return desktops


@router.get("/{desktop_uuid}", responses={status.HTTP_200_OK: {"model": MyBaseSchema[DesktopDetailSchema]},
                                          **CommonResponse.NotFoundErrorResponse})
def get_desktop_detail(desktop_uuid: str):
    """
    指定UUID查询桌面详情.
    """
    manager = DesktopManager()
    desktop = manager.get_desktop_by_uuid(desktop_uuid)
    return desktop


@router.delete("/{desktop_uuid}", responses={status.HTTP_200_OK: {"model": MyBaseSchema[DesktopDetailSchema]},
                                             **CommonResponse.NotFoundErrorResponse})
def delete_desktop(desktop_uuid: str):
    """
    指定UUID删除桌面.
    """
    manager = DesktopManager()
    desktop = manager.delete_desktop_by_uuid(desktop_uuid)
    return desktop


@router.patch("/{desktop_uuid}", responses={status.HTTP_200_OK: {"model": MyBaseSchema[DesktopDetailSchema]},
                                            **CommonResponse.NotFoundErrorResponse})
def patch_desktop(desktop_uuid: str, desktop: DesktopPatchSchema):
    manager = DesktopManager()
    desktop = manager.patch_desktop(desktop_uuid, desktop)
    return desktop
