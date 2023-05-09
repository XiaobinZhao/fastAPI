from typing import List
from fastapi import status
from fastapi import Depends
from myapp.base.schema import MyBaseSchema
from myapp.schema.user import UserBase as UserBaseSchema
from myapp.schema.user import UserDetail as UserDetailSchema
from myapp.schema.user import UserCreate as UserCreateSchema
from myapp.schema.user import UserPatched as UserPatchedSchema
from myapp.manager.user import UserManager
from myapp.base.router import MyRouter
from myapp.manager.token import verify_token
# Depends(verify_token)
router = MyRouter(prefix="/users", tags=["user"], dependencies=[],
                  responses={status.HTTP_401_UNAUTHORIZED: {"model": MyBaseSchema}})


@router.post("/", status_code=status.HTTP_201_CREATED,
             responses={status.HTTP_201_CREATED: {"model": MyBaseSchema[UserDetailSchema]},
                        status.HTTP_409_CONFLICT: {"model": MyBaseSchema}})
async def create_user(user: UserCreateSchema):
    manager = UserManager()
    user = await manager.create_user(user)
    return MyBaseSchema[UserDetailSchema](data=user)


@router.get("/", response_model=MyBaseSchema[List[UserDetailSchema]])
async def list_users(skip: int = 0, limit: int = 100):
    """
    查询用户列表.
    """
    manager = UserManager()
    users = await manager.list_users(skip=skip, limit=limit)
    return MyBaseSchema[List[UserDetailSchema]](data=users)


@router.get("/{user_uuid}", response_model=MyBaseSchema[UserDetailSchema])
async def get_user_detail(user_uuid: str):
    """
    指定UUID查询用户详情.
    """
    manager = UserManager()
    user = await manager.get_user_by_uuid(user_uuid)
    return MyBaseSchema[UserDetailSchema](data=user)

@router.get("/auth/{user_uuid}", response_model=MyBaseSchema[UserDetailSchema])
async def get_user_auth(user_uuid: str):
    """
    指定UUID查询用户权限.
    """
    manager = UserManager()
    user = await manager.get_user_auth_by_uuid(user_uuid)
    return MyBaseSchema[UserDetailSchema](data=user)


@router.delete("/{user_uuid}", response_model=MyBaseSchema)
async def delete_user(user_uuid: str):
    """
    指定UUID删除用户.
    """
    manager = UserManager()
    user = await manager.delete_user_by_uuid(user_uuid)
    return MyBaseSchema(data=user)


@router.patch("/{user_uuid}", response_model=MyBaseSchema[UserDetailSchema])
async def patch_user(user_uuid: str, user: UserPatchedSchema):
    manager = UserManager()
    user = await manager.patch_user(user_uuid, user)
    return MyBaseSchema[UserDetailSchema](data=user)
