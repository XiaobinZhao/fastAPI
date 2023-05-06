from uuid import uuid4
from myapp.models.qa import Qa as DB_Qa_Model
from myapp.base.schema import PageSchema
from myapp.schema.qa import QaBase as QaBaseViewModel
from myapp.exception.qa import QaNotFountException


class QaManager(object):
    def __init__(self, *args, **keywords):
        super(QaManager, self).__init__(*args, **keywords)

    async def list_qas(self, skip: int = 0, limit: int = 100):
        qas = await DB_Qa_Model.async_filter(limit=limit, offset=skip)
        return qas

    async def page_qas(self, skip: int = 0, limit: int = 100):
        qas, total_count = await DB_Qa_Model.async_filter(is_get_total_count=True, limit=limit, offset=skip)
        return PageSchema(total=total_count, limit=limit, skip=skip, data=qas)

    async def create_qa(self, qa: QaBaseViewModel):
        qa = DB_Qa_Model(**qa.dict())
        qa.uuid = uuid4().hex
        qa = await qa.async_create()
        return qa

    async def get_qa_by_uuid(self, qa_uuid):
        qa = DB_Qa_Model(uuid=qa_uuid)
        qa = await qa.async_first(uuid=qa_uuid)
        if not qa:
            raise QaNotFountException(message="Qa %s not found." % qa_uuid)
        return qa

    async def delete_qa_by_uuid(self, qa_uuid):
        row_count = await DB_Qa_Model.async_delete(uuid=qa_uuid)
        if not row_count:
            raise QaNotFountException(message="Qa %s not found." % qa_uuid)
        return None

    async def patch_qa(self, qa_uuid, patched_qa):
        row_count = await DB_Qa_Model.async_update(uuid=qa_uuid, **patched_qa.dict(exclude_unset=True))
        if not row_count:
            raise QaNotFountException(message="Qa %s not found." % qa_uuid)
        qa = await DB_Qa_Model.async_first(uuid=qa_uuid)
        return qa
