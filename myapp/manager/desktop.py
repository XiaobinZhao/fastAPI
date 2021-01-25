from uuid import uuid4
from myapp.models.desktop import Desktop as DB_Desktop_Model
from myapp.schema.desktop import DesktopBase as DesktopBaseViewModel
from myapp.base.exception import NotFountException


class DesktopManager(object):
    def __init__(self, *args, **keywords):
        super(DesktopManager, self).__init__(*args, **keywords)

    def list_desktops(self, skip: int = 0, limit: int = 100):
        desktops = DB_Desktop_Model().get_by_page(skip, limit)
        return desktops

    def create_desktop(self, desktop: DesktopBaseViewModel):
        desktop = DB_Desktop_Model(**desktop.dict())
        desktop.uuid = uuid4().hex
        desktop.vm_uuid = uuid4().hex
        desktop.node_uuid = uuid4().hex
        desktop.node_name = "host1"
        desktop = desktop.add()
        return desktop

    def get_desktop_by_uuid(self, desktop_uuid):
        desktop = DB_Desktop_Model(uuid=desktop_uuid)
        desktop = desktop.get_by_id()
        if not desktop:
            raise NotFountException(message="Desktop %s not found." % desktop_uuid)
        return desktop

    def delete_desktop_by_uuid(self, desktop_uuid):
        desktop = DB_Desktop_Model(uuid=desktop_uuid)
        desktop.delete()
        return None
