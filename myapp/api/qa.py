from typing import List
from fastapi import status
from fastapi import Depends
from myapp.base.schema import MyBaseSchema, PageSchema
from myapp.base.router import MyRouter
from myapp.schema.qa import QaBase as QaBaseSchema
from myapp.schema.qa import QaDetail as QaDetailSchema
from myapp.schema.qa import QaPatch as QaPatchSchema
from myapp.manager.qa import QaManager
from myapp.manager.token import verify_token

router = MyRouter(prefix="/qas", tags=["qa"], dependencies=[],
                  responses={status.HTTP_401_UNAUTHORIZED: {"model": MyBaseSchema}})


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"model": MyBaseSchema[QaDetailSchema]}})
async def create_qa(qa: QaBaseSchema):
    manager = QaManager()
    qa = await manager.create_qa(qa)
    return MyBaseSchema[QaDetailSchema](data=qa)


@router.get("/", response_model=MyBaseSchema[List[QaDetailSchema]])
async def list_qas(skip: int = 0, limit: int = 100):
    """
    查询QA列表.
    """
    manager = QaManager()
    qas = await manager.list_qas(skip=skip, limit=limit)
    return MyBaseSchema[List[QaDetailSchema]](data=qas)


@router.get("/page", response_model=MyBaseSchema[PageSchema[List[QaDetailSchema]]])
async def page_qas(skip: int = 0, limit: int = 10):
    """
    查询QA列表.
    """
    manager = QaManager()
    page_data = await manager.page_qas(skip=skip, limit=limit)
    return MyBaseSchema[PageSchema[List[QaDetailSchema]]](data=page_data)


@router.get("/{qa_uuid}", response_model=MyBaseSchema[QaDetailSchema])
async def get_qa_detail(qa_uuid: str):
    """
    指定UUID查询QA详情.
    """
    manager = QaManager()
    qa = await manager.get_qa_by_uuid(qa_uuid)
    return MyBaseSchema[QaDetailSchema](data=qa)


@router.delete("/{qa_uuid}", response_model=MyBaseSchema)
async def delete_qa(qa_uuid: str):
    """
    指定UUID删除QA.
    """
    manager = QaManager()
    qa = await manager.delete_qa_by_uuid(qa_uuid)
    return MyBaseSchema(data=qa)


@router.patch("/{qa_uuid}", response_model=MyBaseSchema[QaDetailSchema])
async def patch_qa(qa_uuid: str, qa: QaPatchSchema):
    manager = QaManager()
    qa = await manager.patch_qa(qa_uuid, qa)
    return MyBaseSchema[QaDetailSchema](data=qa)
