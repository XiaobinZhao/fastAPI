import time
import json
from loguru import logger
from jose import JWTError, jwt
from fastapi import Depends
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from myapp.base import constant
from myapp.base.exception import UnauthorizedException
from myapp.base.tools import crypt_context
from myapp.models.user import User as DB_User_Model
from myapp.schema.token import TokenPayload
from myapp.base.cache import MyCache
from myapp.manager.user import UserManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, constant.SECRET_KEY, algorithms=[constant.ALGORITHM])
        login_name: str = payload.get("sub")
        if login_name is None:
            raise UnauthorizedException()
        # 缓存用户数据到cache
        if not MyCache.get(login_name)["result"]:
            manager = UserManager()
            user = manager.get_user_by_login_name(login_name)
            if not user:
                raise UnauthorizedException(message="User %s not exist." % login_name)
            result = MyCache.set(login_name, json.dumps(user.as_dict()))
            logger.info("set user to redis result: %s" % result)
        if payload["exp"] < time.time():
            raise UnauthorizedException(message="Token has been expired.")
    except JWTError as e:
        raise UnauthorizedException(message=str(e))


class TokenManager(object):
    def __init__(self, *args, **keywords):
        super(TokenManager, self).__init__(*args, **keywords)

    def create_token(self, user: DB_User_Model):
        token_expires = timedelta(minutes=constant.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire_at = datetime.now() + token_expires
        jwt_payload = TokenPayload(sub=user.login_name, exp=expire_at)
        encoded_jwt = jwt.encode(jwt_payload.dict(), constant.SECRET_KEY, algorithm=constant.ALGORITHM)
        return encoded_jwt, expire_at

    def verify_password(self, plain_password, hashed_password):
        if not crypt_context.verify(plain_password, hashed_password):
            raise UnauthorizedException(message="Incorrect username or password.",
                                        headers={"WWW-Authenticate": "Bearer"})

