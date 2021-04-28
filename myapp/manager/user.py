import json
from uuid import uuid4
from loguru import logger
from myapp.models.user import User as DB_User_Model
from myapp.schema.user import UserCreate as UserCreateViewModel
from myapp.exception.user import UserNotFountException
from myapp.base.tools import crypt_context
from myapp.exception.user import UserLoginNameExistException
from myapp.base.cache import MyCache


class UserManager(object):
    def __init__(self, *args, **keywords):
        super(UserManager, self).__init__(*args, **keywords)

    async def list_users(self, skip: int = 0, limit: int = 100):
        users = await DB_User_Model.async_filter(offset=skip, limit=limit)
        return users

    async def create_user(self, user: UserCreateViewModel):
        is_exists_same_user = await DB_User_Model.async_filter(login_name=user.login_name)
        if is_exists_same_user:
            raise UserLoginNameExistException()
        user = DB_User_Model(**user.dict())
        user.uuid = uuid4().hex
        user.password = crypt_context.hash(user.password)  # 加密密码
        user = await user.async_create()
        return user

    async def get_user_by_uuid(self, user_uuid):
        user = await DB_User_Model.async_first(uuid=user_uuid)
        if not user:
            raise UserNotFountException(message="User %s not found." % user_uuid)
        return user

    async def get_user_by_login_name(self, login_name):
        user = await DB_User_Model.async_first(login_name=login_name)
        if not user:
            raise UserNotFountException(message="User %s not found." % login_name)
        return user

    async def delete_user_by_uuid(self, user_uuid):
        user = await DB_User_Model.async_delete(uuid=user_uuid)
        if not user:
            raise UserNotFountException(message="User %s not found." % user_uuid)
        result = MyCache.remove(user_uuid)
        logger.info("redis delete result: %s" % result)
        return None

    async def patch_user(self, user_uuid, patched_user):
        row_count = await DB_User_Model.async_update(uuid=user_uuid, **patched_user.dict(exclude_unset=True))
        if not row_count:
            raise UserNotFountException(message="User %s not found." % user_uuid)
        user = await DB_User_Model.async_first(uuid=user_uuid)
        result = MyCache.set(user_uuid, json.dumps(user.to_dict()))
        logger.info("redis update result: %s" % result)
        return user
