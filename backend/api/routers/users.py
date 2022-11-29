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

from typing import List, Optional

from externals.userRole import UserRole

from db import crud

from .. import schemas


def verify_token(token: str = Header(), session: Session = Depends(get_session)):
    user = crud.get_user_by_token(token, session)
    if not user or user.role != "ADMIN":
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)


router = APIRouter(tags=["user"], dependencies=[Depends(verify_token)])


@router.patch("/user/{id}", response_model=schemas.User)
async def update_user(
    id,
    name: Optional[str] = Form(None),
    role: Optional[UserRole] = Form(None),
    profile_pic: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
):
    profile_pic_name = profile_pic.filename.split(".")[-1] if profile_pic else None
    user = await crud.update_user(
        {"id": id, "name": name, "role": role},
        profile_pic_name,
        session,
    )
    if profile_pic:
        file_location = user.profile_pic
        with open(file_location, "wb+") as file_object:
            file_object.write(profile_pic.file.read())

    return user


@router.get("/user/{token_search}", response_model=schemas.User)
def get_user_by_token(token, session: Session = Depends(get_session)):
    user = crud.get_user_by_token(token, session)
    if not user:
        raise HTTPException(404)
    return user


@router.get("/users", response_model=List[schemas.User])
def get_all_users(session: Session = Depends(get_session)):
    return crud.get_all_users(session)
