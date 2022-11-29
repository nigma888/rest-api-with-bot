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
    if not user or user.role != "ADMIN":
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)


router = APIRouter(tags=["token"])


@router.get("/token_useragentcc")
def get_useragentcc_token():
    with open("tokens/token_useragentcc.txt", "r") as f:
        line = f.read()
    return line.strip()


@router.get("/token_tablecrm")
def get_tablecrm_token():
    with open("tokens/token_tablecrm.txt", "r") as f:
        line = f.read()
    return line.strip()


@router.put("/token_useragentcc", dependencies=[Depends(verify_token)])
def update_useragentcc_token(request: schemas.UpdateToken):
    request = request.dict()
    with open("tokens/token_useragentcc.txt", "w") as f:
        f.write(request["data"])
    return "succesful"


@router.put("/token_tablecrm", dependencies=[Depends(verify_token)])
def update_tablecrm_token(request: schemas.UpdateToken):
    request = request.dict()
    with open("tokens/token_tablecrm.txt", "w") as f:
        f.write(request["data"])
    return "succesful"
