import json
from typing import List
from typing import Callable
from fastapi import APIRouter
from fastapi import status
from fastapi import Response
from fastapi import Request
from fastapi.routing import APIRoute

from myapp.base.schema import ResponseModel
from myapp.schema import desktop as desktop_schema
from myapp.manager.desktop import DesktopManager


class CustomResponseRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            response: Response = await original_route_handler(request)
            response_body = json.loads(response.body.decode())
            custome_response = ResponseModel(data=response_body)
            response.body = json.dumps(custome_response.dict()).encode()
            for index, value in enumerate(response.headers.raw):
                if b'content-length' in value:
                    response.headers.raw[index] = (b'content-length', str(len(response.body)).encode())

            return response

        return custom_route_handler


router = APIRouter(prefix="/desktops", tags=["desktop"], route_class=CustomResponseRoute)


def wrapSchema(schema, type="object"):
    after_update = ResponseModel.schema()
    if type == "array":
        after_update["properties"]["data"].update({"type": "array", "items": schema.schema()})
    else:
        after_update["properties"]["data"].update(schema.schema())
    return {"content":
                {"application/json":
                     {"schema": after_update}
                 }
            }


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: wrapSchema(desktop_schema.DesktopDetail),
                        status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseModel}})
def create_desktop(desktop: desktop_schema.DesktopBase):
    manager = DesktopManager()
    desktop = manager.create_desktop(desktop)
    return desktop


@router.get("/", responses={status.HTTP_200_OK: wrapSchema(desktop_schema.DesktopDetail, "array"),
                            status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseModel}})
def list_desktops(skip: int = 0, limit: int = 100):
    """
    查询桌面列表.
    """
    manager = DesktopManager()
    desktops = manager.list_desktops(skip=skip, limit=limit)
    return desktops


@router.get("/{desktop_uuid}", responses={status.HTTP_200_OK: wrapSchema(desktop_schema.DesktopDetail),
                                          status.HTTP_404_NOT_FOUND: {"model": ResponseModel},
                                          status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseModel}})
def get_desktop_detail(desktop_uuid: str):
    """
    指定UUID查询桌面详情.
    """
    manager = DesktopManager()
    desktop = manager.get_desktop_by_uuid(desktop_uuid)
    return desktop


@router.delete("/{desktop_uuid}", responses={status.HTTP_200_OK: {"model": ResponseModel},
                                             status.HTTP_422_UNPROCESSABLE_ENTITY: {"model": ResponseModel}})
def delete_desktop(desktop_uuid: str):
    """
    指定UUID删除桌面.
    """
    manager = DesktopManager()
    desktop = manager.delete_desktop_by_uuid(desktop_uuid)
    return desktop
