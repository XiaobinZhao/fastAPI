from uuid import uuid4

from myapp.base.snowflake import IDWorker

from myapp.models.desktop import Desktop as DB_Desktop_Model
from myapp.base.schema import PageSchema
from myapp.schema.desktop import DesktopBase as DesktopBaseViewModel
from myapp.exception.desktop import DesktopNotFountException


class DesktopManager(object):
    def __init__(self, *args, **keywords):
        super(DesktopManager, self).__init__(*args, **keywords)

    @staticmethod
    async def list_desktops(search_key: str = "", search_str: str = "", filters=None):
        desktops = await DB_Desktop_Model.async_filter(is_get_total_count=False, search_key=search_key,
                                                       search_str=search_str, **filters)
        return desktops

    @staticmethod
    async def page_desktops(search_key: str = "", search_str: str = "", filters=None, skip: int = 0, limit: int = 100):
        desktops, total_count = await DB_Desktop_Model.async_filter(is_get_total_count=True, search_key=search_key,
                                                                    search_str=search_str, offset=skip,
                                                                    limit=limit, **filters)
        return PageSchema(total=total_count, limit=limit, skip=skip, data=desktops)

    @staticmethod
    async def create_desktop(desktop: DesktopBaseViewModel):
        desktop = DB_Desktop_Model(**desktop.dict())
        desktop.uuid = IDWorker.gen_id()
        desktop.vm_uuid = uuid4().hex
        desktop.node_uuid = uuid4().hex
        desktop.node_name = "host1"
        desktop = await desktop.async_create()
        return desktop

    @staticmethod
    async def get_desktop_by_uuid(desktop_uuid):
        desktop = DB_Desktop_Model(uuid=desktop_uuid)
        desktop = await desktop.async_first(uuid=desktop_uuid)
        if not desktop:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        return desktop

    @staticmethod
    async def delete_desktop_by_uuid(desktop_uuid):
        row_count = await DB_Desktop_Model.async_delete(uuid=desktop_uuid)
        if not row_count:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        return None

    @staticmethod
    async def patch_desktop(desktop_uuid, patched_desktop) -> DB_Desktop_Model:
        row_count = await DB_Desktop_Model.async_update_by_uuid(uuid=desktop_uuid,
                                                                **patched_desktop.dict(exclude_unset=True))
        if not row_count:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        desktop = await DB_Desktop_Model.async_first(uuid=desktop_uuid)
        return desktop
