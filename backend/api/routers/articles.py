from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    HTTPException,
    Header,
    status,
    Query,
)
from db.database import get_session
from sqlalchemy.orm import Session


from typing import List, Optional
from datetime import datetime

from externals.userRole import UserRole

from db import crud

from .. import schemas


def verify_token(
    token: str = Header(),
    session: Session = Depends(get_session),
):
    user = crud.get_user_by_token(token, session)
    if not user:
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)
    if user.role == "ADMIN":
        return user, 3
    elif user.role == "COPYWRITER":
        return user, 2
    return user, 1


router = APIRouter(tags=["article"])


@router.get(
    "/article",
    response_model=List[schemas.Article],
)
def get_all_articles(
    tags_ids: List[int] = Query([]),
    categories_ids: List[int] = Query([]),
    performers_ids: List[int] = Query([]),
    contragents_ids: List[int] = Query([]),
    contragents_names: List[str] = Query([]),
    limit: int = Query(None),
    offset: int = Query(None),
    session: Session = Depends(get_session),
):

    # user, lvl_access = verify
    # if lvl_access < 3:
    #     return user.articles
    items = crud.get_all_article(
        session,
        limit,
        offset,
        tags_ids,
        categories_ids,
        performers_ids,
        contragents_ids,
        contragents_names,
    )
    return items


@router.post("/article", response_model=schemas.Article)
async def create_article(
    title: str = Form(None),
    first_sentence: str = Form(None),
    content: str = Form(None),
    price_hour: float = Form(None),
    owner: int = Form(None),
    tags: Optional[List[int]] = Form([]),
    category: Optional[List[int]] = Form([]),
    client_tablecrm: str = Form(None),
    client_tablecrm_id: int = Form(None),
    seo_url: str = Form(None),
    project_tablecrm: str = Form(None),
    project_tablecrm_id: int = Form(None),
    performer: int = Form(None),
    isPublic: bool = Form(False),
    isPublish: bool = Form(False),
    header_image: UploadFile = File(None),
    main_image: UploadFile = File(None),
    session: Session = Depends(get_session),
    verify=Depends(verify_token),
):
    user, lvl_access = verify

    main_image_name = main_image.filename.split(".")[-1] if main_image else None
    header_image_name = header_image.filename.split(".")[-1] if header_image else None
    article = await crud.create_article(
        {
            "title": title,
            "first_sentence": first_sentence,
            "content": content,
            "owner": owner,
            "tags": tags,
            "price_hour": price_hour,
            "category": category,
            "client_tablecrm": client_tablecrm,
            "client_tablecrm_id": client_tablecrm_id,
            "seo_url": seo_url,
            "project_tablecrm": project_tablecrm,
            "project_tablecrm_id": project_tablecrm_id,
            "isPublic": isPublic,
            "isPublish": isPublish,
            "time_updated": datetime.now(),
            "performer": performer,
        },
        main_image_name,
        header_image_name,
        session,
    )
    if header_image:
        file_location = (
            f"images/header_pic/{article.id}.{header_image.filename.split('.')[-1]}"
        )
        with open(file_location, "wb+") as file_object:
            file_object.write(header_image.file.read())
    if main_image:
        file_location = (
            f"images/main_pic/{article.id}.{main_image.filename.split('.')[-1]}"
        )
        with open(file_location, "wb+") as file_object:
            file_object.write(main_image.file.read())

    return article


@router.patch("/article/{id}", response_model=schemas.Article)
async def update_article(
    id: int,
    title: Optional[str] = Form(None),
    first_sentence: Optional[str] = Form(None),
    content: Optional[str] = Form(None),
    price_hour: Optional[float] = Form(None),
    tags: Optional[List[int]] = Form([]),
    category: Optional[List[int]] = Form([]),
    client_tablecrm: Optional[str] = Form(None),
    client_tablecrm_id: Optional[int] = Form(None),
    project_tablecrm: Optional[str] = Form(None),
    project_tablecrm_id: Optional[int] = Form(None),
    seo_url: Optional[str] = Form(None),
    performer: Optional[int] = Form(None),
    isPublic: Optional[bool] = Form(None),
    isPublish: Optional[bool] = Form(None),
    header_image: Optional[UploadFile] = File(None),
    main_image: Optional[UploadFile] = File(None),
    session: Session = Depends(get_session),
    verify=Depends(verify_token),
):
    user, lvl_access = verify
    article = crud.get_article_by_id(id, session)
    if lvl_access >= 2 or article.owner == user:
        main_image_name = main_image.filename.split(".")[-1] if main_image else None
        header_image_name = (
            header_image.filename.split(".")[-1] if header_image else None
        )
        article = await crud.update_article(
            {
                "id": id,
                "title": title,
                "first_sentence": first_sentence,
                "content": content,
                "tags": tags,
                "price_hour": price_hour,
                "category": category,
                "client_tablecrm": client_tablecrm,
                "client_tablecrm_id": client_tablecrm_id,
                "seo_url": seo_url,
                "isPublic": isPublic,
                "isPublish": isPublish,
                "project_tablecrm": project_tablecrm,
                "project_tablecrm_id": project_tablecrm_id,
                "performer": performer,
                "time_updated": datetime.now(),
            },
            main_image_name,
            header_image_name,
            session,
        )
        if header_image:
            file_location = (
                f"images/header_pic/{article.id}.{header_image.filename.split('.')[-1]}"
            )
            with open(file_location, "wb+") as file_object:
                file_object.write(header_image.file.read())
        if main_image:
            file_location = (
                f"images/main_pic/{article.id}.{main_image.filename.split('.')[-1]}"
            )
            with open(file_location, "wb+") as file_object:
                file_object.write(main_image.file.read())
        return article
    else:
        raise HTTPException(status.HTTP_405_METHOD_NOT_ALLOWED)
