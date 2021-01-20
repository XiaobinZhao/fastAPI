from typing import List
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from myapp.base.dependency.db import get_db_session
from myapp.models import Desktop
from myapp.schema import desktop as desktop_schema
from myapp.manager.desktop import DesktopManager

router = APIRouter(prefix="/desktops", tags=["desktop"])


def create_desktop(db: Session, desktop: desktop_schema.DesktopBase, user_id: int):
    db_desktop = Desktop(**desktop.dict())
    db.add(db_desktop)
    db.commit()
    db.refresh(db_desktop)
    return db_desktop


@router.post("/", response_model=desktop_schema.DesktopDetail)
def create_desktop(desktop: desktop_schema.DesktopBase):
    manager = DesktopManager()
    desktop = manager.create_desktop(desktop)
    return desktop


@router.get("/", response_model=List[desktop_schema.DesktopDetail])
def list_desktops(skip: int = 0, limit: int = 100):
    """
    查询桌面.
    """
    manager = DesktopManager()
    desktops = manager.list_desktops(skip=skip, limit=limit)
    return desktops
