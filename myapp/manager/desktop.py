from uuid import uuid4
from myapp.models.desktop import Desktop as DB_Desktop_Model
from myapp.schema.desktop import DesktopBase as DesktopBaseViewModel
from myapp.exception.desktop import DesktopNotFountException


class DesktopManager(object):
    def __init__(self, *args, **keywords):
        super(DesktopManager, self).__init__(*args, **keywords)

    async def list_desktops(self, skip: int = 0, limit: int = 100):
        desktops = await DB_Desktop_Model.async_filter(limit=limit, offset=skip)
        return desktops

    async def create_desktop(self, desktop: DesktopBaseViewModel):
        desktop = DB_Desktop_Model(**desktop.dict())
        desktop.uuid = uuid4().hex
        desktop.vm_uuid = uuid4().hex
        desktop.node_uuid = uuid4().hex
        desktop.node_name = "host1"
        desktop = await desktop.async_create()
        return desktop

    async def get_desktop_by_uuid(self, desktop_uuid):
        desktop = DB_Desktop_Model(uuid=desktop_uuid)
        desktop = await desktop.async_first(uuid=desktop_uuid)
        if not desktop:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        return desktop

    async def delete_desktop_by_uuid(self, desktop_uuid):
        row_count = await DB_Desktop_Model.async_delete(uuid=desktop_uuid)
        if not row_count:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        return None

    async def patch_desktop(self, desktop_uuid, patched_desktop):
        row_count = await DB_Desktop_Model.async_update(uuid=desktop_uuid, **patched_desktop.dict(exclude_unset=True))
        if not row_count:
            raise DesktopNotFountException(message="Desktop %s not found." % desktop_uuid)
        desktop = await DB_Desktop_Model.async_first(uuid=desktop_uuid)
        return desktop
