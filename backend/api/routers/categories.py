from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Header,
    status,
)
from db.database import get_session
from sqlalchemy.orm import Session


from typing import List

from externals.userRole import UserRole

from db import crud

from .. import schemas


def verify_token(token: str = Header(), session: Session = Depends(get_session)):
    user = crud.get_user_by_token(token, session)
    if not user or (user.role != "ADMIN" and user.role != "COPYWRITER"):
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)


router = APIRouter(tags=["category"], dependencies=[Depends(verify_token)])


@router.post("/category", response_model=schemas.TagResponse)
def create_category(request: schemas.Tag, session: Session = Depends(get_session)):
    return crud.create_category(request.dict(), session)


@router.get("/category", response_model=schemas.TagList)
def get_all_category(session: Session = Depends(get_session)):
    items = crud.get_all_category(session)
    return schemas.TagList(items=items)
