from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from myapp.base.router import MyRouter
from myapp.schema.token import Token
from myapp.manager.user import UserManager
from myapp.manager.token import TokenManager

router = MyRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    用户名/密码登录。成功返回token
    """
    user_manager = UserManager()
    user = user_manager.get_user_by_login_name(form_data.username)
    token_manager = TokenManager()
    token_manager.verify_password(form_data.password, user.password)
    encode_token, expire_at, created_at = token_manager.create_token(user)

    return Token(access_token=encode_token, user_uuid=user.uuid, expired_at=expire_at, created_at=created_at)
