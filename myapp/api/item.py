# from fastapi import APIRouter
#
# from myapp.models.item import Item
# from myapp.schema.item import ItemCreate
# from typing import List
#
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from myapp.schema import item as item_schema
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
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(Item).offset(skip).limit(limit).all()
#
#
# def create_user_item(db: Session, item: ItemCreate, user_id: int):
#     db_item = Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
#
#
# @router.post("/users/{user_id}/items/", response_model=item_schema.Item, tags=["item"])
# def create_item_for_user(
#     user_id: int, item: item_schema.ItemCreate, db: Session = Depends(get_db)
# ):
#     return create_user_item(db=db, item=item, user_id=user_id)
#
#
# @router.get("/items/", response_model=List[item_schema.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = get_items(db, skip=skip, limit=limit)
#     return items
