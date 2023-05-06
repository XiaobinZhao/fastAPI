import json
from uuid import uuid4
from loguru import logger
from myapp.base.tools import crypt_context
from myapp.schema.jjtest import JjtesCreate as QuestionCreateViewModel
from myapp.models.jjtest import Jjtest as DB_Question_Model
from myapp.exception.jjtest import QuestionLoginNameExistException
from myapp.exception.jjtest import QuestionNotFountException
from myapp.base.cache import MyCache

class JjtestManager(object):
    def __init__(self, *args, **keywords):
        super(JjtestManager, self).__init__(*args, **keywords)
        
    async def list_questions(self, skip: int = 0, limit: int = 100):
        questions = await DB_Question_Model.async_filter(offset=skip, limit=limit)
        return questions
        
    async def create_question(self, question: QuestionCreateViewModel):
        is_existes_same_question = await DB_Question_Model.async_filter(login_name=question.login_name)
        if is_existes_same_question:
            raise QuestionLoginNameExistException()
        question = DB_Question_Model(**question.dict())
        question.uuid = uuid4().hex
        question.password = crypt_context.hash(question.password)	# 加密密码
        question = await question.async_create()
        return question
    
    async def delete_question_by_uuid(self, question_uuid):
        question = await DB_Question_Model.async_delete(uuid=question_uuid)
        if not question:
            raise QuestionNotFountException()
        result = await MyCache.remove(question_uuid)
        logger.info('redis delete result: %s' % result)
        return None
    
    async def patch_question(self, question_uuid, patched_question):
        row_count = await DB_Question_Model.async_update(uuid=question_uuid, **patched_question.dict(exclude_unset=True))
        if not row_count:
            raise QuestionNotFountException(message="Question %s not found." % question_uuid)
        question = await DB_Question_Model.async_first(uuid=question_uuid)
        result = await MyCache.set(question_uuid, json.dumps(question.to_dict()))
        logger.info("redis update result: %s" % result)
        return question
    
    async def get_question_by_uuid(self, question_uuid):
        question = await DB_Question_Model.async_first(uuid=question_uuid)
        if not question:
            raise QuestionNotFountException(message="Question %s not found." % question_uuid)
        return question
            
            
    

        