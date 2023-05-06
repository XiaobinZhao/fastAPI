
from typing import List
from fastapi import Depends
from fastapi import status
from myapp.base.schema import MyBaseSchema
from myapp.schema.jjtest import JjtestDetail as JjtestDetailSchema
from myapp.schema.jjtest import JjtesCreate as JjtestCreateSchema
from myapp.schema.jjtest import JjtestPatched as JjtestPatchedSchema

from myapp.manager.jjtest import JjtestManager

from myapp.base.router import MyRouter
from myapp.manager.token import verify_token

router = MyRouter(prefix="/jjtest", tags=['jj'], dependencies=[Depends(verify_token)],
                  responses={status.HTTP_401_UNAUTHORIZED: {'model': MyBaseSchema}})

@router.post('/', status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {'model': MyBaseSchema[JjtestDetailSchema]},
                        status.HTTP_409_CONFLICT: {'model': MyBaseSchema}})
async def create_question(question: JjtestCreateSchema):
    manager = JjtestManager()
    question = await manager.create_question(question)
    return MyBaseSchema[JjtestDetailSchema](data=question)

@router.get('/', response_model=MyBaseSchema[List[JjtestDetailSchema]])
async def list_questions(skip: int = 0, limit: int = 100):
    """
    查询问题列表
    """
    manager = JjtestManager()
    questions = await manager.list_questions(skip=skip, limit=limit)
    return MyBaseSchema[List[JjtestDetailSchema]](data=questions)

@router.get('/{question_uuid}', response_model=MyBaseSchema[JjtestDetailSchema])
async def get_question_detail(question_uuid: str):
    """
    查询指定问题UUID详情
    """
    manager = JjtestManager()
    question = await manager.get_question_by_uuid(question_uuid)
    return MyBaseSchema[JjtestDetailSchema](data=question)

@router.delete('/{question_uuid}', response_model=MyBaseSchema)
async def delete_question(question_uuid: str):
    """
    删除指定问题UUID详情
    """
    manager = JjtestManager()
    question = await manager.delete_question_by_uuid(question_uuid)
    return MyBaseSchema(data=question)

@router.patch('/{question_uuid}', response_model=MyBaseSchema[JjtestDetailSchema])
async def patch_question(question_uuid: str, question: JjtestPatchedSchema):
    manager = JjtestManager()
    question = await manager.patch_question(question_uuid, question)
    return MyBaseSchema[JjtestDetailSchema](data=question)