# from typing import List
# from sqlalchemy.orm import Session
# from fastapi import HTTPException
# from fastapi import APIRouter
# from fastapi import Depends
# from fastapi import Request
# from myapp.models.user import User
# from myapp.schema import user as user_schema
# from myapp.base.db import DB_SESSION
#
# router = APIRouter()
#
#
# # Dependency
# def get_db():
#     db = DB_SESSION
#     try:
#         yield db
#     finally:
#         db.close()
#
#
# def db_get_user(db: Session, user_id: int):
#     return db.query(User).filter(User.id == user_id).first()
#
#
# def db_get_user_by_email(db: Session, email: str):
#     return db.query(User).filter(User.email == email).first()
#
#
# def db_get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(User).offset(skip).limit(limit).all()
#
#
# def db_create_user(db: Session, user: user_schema.UserCreate):
#     fake_hashed_password = user.password + "notreallyhashed"
#     db_user = User(email=user.email, hashed_password=fake_hashed_password)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user
#
#
# @router.post("/", response_model=user_schema.User)
# def create_user(user: user_schema.UserCreate, db: Session = Depends(get_db)):
#     """
#     创建用户
#     """
#     db_user = db_get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     users_mode = db_create_user(db=db, user=user)
#     return users_mode
#
#
# @router.get("/", response_model=List[user_schema.User])
# def read_users(request: Request, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = db_get_users(db, skip=skip, limit=limit)
#     return users
#
#
# @router.get("/{user_id}", response_model=user_schema.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = db_get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user
