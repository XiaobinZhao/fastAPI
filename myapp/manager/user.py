import json
from uuid import uuid4
from loguru import logger
from myapp.models.user import User as DB_User_Model
from myapp.schema.user import UserCreate as UserCreateViewModel
from myapp.base.exception import NotFountException
from myapp.base.tools import crypt_context
from myapp.exception.user import UserLoginNameExistException
from myapp.base.cache import MyCache


class UserManager(object):
    def __init__(self, *args, **keywords):
        super(UserManager, self).__init__(*args, **keywords)

    def list_users(self, skip: int = 0, limit: int = 100):
        users = DB_User_Model().get_by_page(skip, limit)
        return users

    def create_user(self, user: UserCreateViewModel):
        user = DB_User_Model(**user.dict())
        is_exists_same_user = user.get_by_conditions(login_name=user.login_name)
        if is_exists_same_user:
            raise UserLoginNameExistException()
        user.uuid = uuid4().hex
        user.password = crypt_context.hash(user.password)  # 加密密码
        user = user.add()
        return user

    def get_user_by_uuid(self, user_uuid):
        user = DB_User_Model(uuid=user_uuid)
        user = user.get_by_id()
        if not user:
            raise NotFountException(message="User %s not found." % user_uuid)
        return user

    def get_user_by_login_name(self, login_name):
        user = DB_User_Model()
        user = user.get_by_conditions(login_name=login_name)
        if not user:
            raise NotFountException(message="User %s not found." % login_name)
        return user

    def delete_user_by_uuid(self, user_uuid):
        user = DB_User_Model(uuid=user_uuid)
        user = user.get_by_id()
        if not user:
            raise NotFountException(message="User %s not found." % user_uuid)
        user.delete()
        result = MyCache.remove(user_uuid)
        logger.info("redis delete result: %s" % result)
        return None

    def patch_user(self, user_uuid, patched_user):
        user = DB_User_Model(uuid=user_uuid)
        user = user.get_by_id()
        if not user:
            raise NotFountException(message="User %s not found." % user_uuid)
        for key, value in patched_user.dict(exclude_unset=True).items():
            setattr(user, key, value)
        user.update()
        result = MyCache.set(user_uuid, json.dumps(user.as_dict()))
        logger.info("redis update result: %s" % result)
        return user
