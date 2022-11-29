from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session

from db.database import get_session
from db.functions.files import create_file, get_file_list, get_file_by_id
from api import schemas

import aiofiles
import secrets
import os

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=schemas.File)
async def create_file_route(upload_file: UploadFile = File(...), session: Session = Depends(get_session)):
    hash = secrets.token_urlsafe(16)
    file_link = f"storage/{hash}.{upload_file.filename.split('.')[-1]}"
    file_bytes = await upload_file.read()

    try:
        async with aiofiles.open(file_link, "+wb") as file:
            await file.write(file_bytes)
    finally:
        await upload_file.close()

    return create_file(
        session=session,
        name=upload_file.filename,
        hash=hash,
        link=file_link,
        type=upload_file.content_type,
        file_size=round(len(file_bytes) / 1024, 2)
    )


@router.get("/", response_model=schemas.FileList)
def get_file_list_route(
        names: List[str] = Query([]),
        limit: int = Query(10),
        page: int = Query(1),
        show_delete: bool = Query(True),
        session: Session = Depends(get_session)
):
    return get_file_list(names=names, limit=limit, page=page, show_delete=show_delete, session=session)


@router.get("/{id}", response_model=schemas.File)
def get_file_route(id: int, session: Session = Depends(get_session)):
    return get_file_by_id(session=session, id=id)


@router.delete("/{id}", response_model=schemas.File)
def delete_file_route(id: int, session: Session = Depends(get_session)):
    file = get_file_by_id(id=id, session=session)

    try:
        os.remove(file.link)
    except:
        raise HTTPException(
            status_code=500, detail="Ошибка удаления файла"
        )

    file.is_deleted = True
    session.commit()
    return file
