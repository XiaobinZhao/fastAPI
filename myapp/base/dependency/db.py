from myapp.base.db import SessionFactory


def get_db_session():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()
