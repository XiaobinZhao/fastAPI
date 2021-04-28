import json
import base64
from uuid import uuid4
from loguru import logger
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
    """
    这里不使用OAuth2的token方案。因为OAth2的token方案相对复杂，且考虑到与第三方对接。尤其token refresh的过程：
    1. login得到access_token 和 refresh_token,refresh_token比access_token的有效期更长
    2. 客户端请求使用access_token，如果过期，客户端使用refresh_token再次请求得到新的access_token。
       当然这里也可以返回新的refresh_token，新的refresh_token可以有新的过期时间
    3. 如果access_token过期，并且refresh_token也过期，那么需要重新登录。

    以上方案略显复杂。重新设计如下：
    1. login得到access_token,这个token不使用jwt格式，使用AES非对称加密算法，公钥加密得到token，加密的内容是user_name和uuid
    2. 客户端使用access_token请求，成功之后，会更新过期时间,token不变，新的过期时间为当前时间+有效时长（默认5分钟）
    3. 只要客户端一直请求（请求之间间隔最长不超过5分钟），那么token就一直有效
    此方案优点：
    1. token请求之后，在不间断操作下会一直有效，不用客户端不断refresh
    2. 逻辑简单
    3. token包含了一些信息，可以进行解密读取
    缺点：
    1. 需要保存会话信息，即需依赖redis这样的server端存储token和其过期时间点
    """
    if not MyCache.get(token):
        raise UnauthorizedException(message="Token is invalid or has been expired.")
    else:
        try:
            payload = json.loads(base64.b64decode(token))
        except Exception as e:
            raise UnauthorizedException(message=str(e))
        user_uuid: str = payload.get("user_uuid")
        if user_uuid is None:
            raise UnauthorizedException("Token is invalid.")
        # 缓存用户数据到cache
        if not MyCache.get(user_uuid)["result"]:
            manager = UserManager()
            user = manager.get_user_by_uuid(user_uuid)
            if not user:
                raise UnauthorizedException(message="User %s not exist." % user_uuid)
            MyCache.set(user_uuid, json.dumps(user.as_dict(["password"])))
            logger.info("cache missing, set user: %s to redis" % user_uuid)
    # 更新redis缓存时长，单位s
    MyCache.expire(token, time=constant.ACCESS_TOKEN_EXPIRE_MINUTES * 60)


class TokenManager(object):
    def __init__(self, *args, **keywords):
        super(TokenManager, self).__init__(*args, **keywords)

    def create_token(self, user: DB_User_Model):
        """
        token的生成方式有多种，比如jwt;非对称加密字符串；但是 jwt加密字符串过长且jwt本身的方案特性本系统没有采用；
        非对称AES加密又消耗时间过长，经验证加密一个字符串需要500ms左右。这行的话login API的耗时要达到1s,太长。所以简化为：
        生成带有uuid的字符串，然后使用base64加密得到token。这样token可以保持唯一性（因为uuid），也可以在客户端反解出来得到token
        的内容；后端把token存入redis，作为登录凭证。
        """
        token_expires = timedelta(minutes=constant.ACCESS_TOKEN_EXPIRE_MINUTES)
        jwt_payload = TokenPayload(uuid=uuid4().hex, login_name=user.login_name, user_uuid=user.uuid)
        encoded_payload = base64.b64encode(json.dumps(jwt_payload.dict()).encode(encoding="utf-8"))
        create_at = datetime.now()
        expire_at = create_at + token_expires
        MyCache.set(encoded_payload, json.dumps(user.to_dict(except_keys=["password"])),
                    ex=constant.ACCESS_TOKEN_EXPIRE_MINUTES * 60)  # redis缓存时长，单位s
        return encoded_payload, expire_at, create_at

    def verify_password(self, plain_password, hashed_password):
        if not crypt_context.verify(plain_password, hashed_password):
            raise UnauthorizedException(message="Incorrect username or password.",
                                        headers={"WWW-Authenticate": "Bearer"})

