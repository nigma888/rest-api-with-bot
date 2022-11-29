from sqlalchemy.orm import Session
from db.models import File
from sqlalchemy import or_, func, and_
import math


def create_file(session: Session, **kwargs):
    file = File(**kwargs)
    session.add(file)
    session.commit()
    return file


def get_file_list(limit: int, page: int, show_delete: bool, session: Session, names=None):
    storage = (
        session.query(func.sum(File.file_size))
        .filter(
            or_(File.name.in_(names), not names),
            or_(File.is_deleted.is_not(True if not show_delete else None))
        )
        .scalar()
    )
    count = (
        session.query(File)
        .filter(
            or_(File.name.in_(names), not names),
            or_(File.is_deleted.is_not(True if not show_delete else None))
        )
        .count()
    )
    files = (
        session.query(File)
        .filter(
            or_(File.name.in_(names), not names),
            or_(File.is_deleted.is_not(True if not show_delete else None))
        )
        .limit(limit)
        .offset((page-1) * limit + 1)
        .all()
    )

    return {
        "files": files,
        "count": count,
        "pages": math.ceil(count / limit) if limit != 0 else count,
        "storage": storage
    }


def get_file_by_id(id: int, session: Session):
    return session.query(File).get(id)
