from typing import List
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from myapp.base.dependency.db import get_db_session
from myapp.models import Desktop
from myapp.schema import desktop as desktop_schema
from myapp.main import app
router = APIRouter()


def get_desktops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Desktop).offset(skip).limit(limit).all()


def create_desktop(db: Session, desktop: desktop_schema.DesktopBase, user_id: int):
    db_desktop = Desktop(**desktop.dict())
    db.add(db_desktop)
    db.commit()
    db.refresh(db_desktop)
    return db_desktop


@app.post("/desktops/", response_model=desktop_schema.DesktopDetail, tags=["desktop"])
def create_desktop(
    user_id: int, desktop: desktop_schema.DesktopBase, db: Session = Depends(get_db_session)
):
    return create_desktop(db=db, desktop=desktop, user_id=user_id)


@app.get("/desktops/", response_model=List[desktop_schema.DesktopDetail])
def read_desktops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    desktops = get_desktops(db, skip=skip, limit=limit)
    return desktops
