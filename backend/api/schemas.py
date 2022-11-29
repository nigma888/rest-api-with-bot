from pydantic import BaseModel
from typing import List, Optional, Union
import datetime

from externals.userRole import UserRole


class Tag(BaseModel):
    name: str


class TagResponse(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class TagList(BaseModel):
    items: List[TagResponse]

    class Config:
        orm_mode = True


class File(BaseModel):
    id: int
    name: str
    hash: str
    link: str
    type: str
    file_size: str
    is_deleted: bool

    created_at: datetime.datetime
    updated_at: Union[datetime.datetime, None]

    class Config:
        orm_mode = True


class FileList(BaseModel):
    files: List[File]
    count: int
    pages: int
    storage: str


class User(BaseModel):
    id: int
    name: str

    role: UserRole
    profile_pic: Optional[str]

    class Config:
        orm_mode = True


class Article(BaseModel):
    id: int
    title: Optional[str]
    first_sentence: Optional[str]
    content: Optional[str]
    isPublic: bool
    isPublish: bool
    header_pic: Optional[str]
    main_pic: Optional[str]
    tags: Optional[List[TagResponse]]
    category: Optional[List[TagResponse]]
    client_tablecrm: Optional[str]
    client_tablecrm_id: Optional[int]

    seo_url: Optional[str]

    time_created: Optional[datetime.datetime]
    time_updated: Optional[datetime.datetime]

    project_tablecrm: Optional[str]
    project_tablecrm_id: Optional[int]

    price_hour: Optional[float]
    performer: Optional[User]
    owner: Optional[User]

    class Config:
        orm_mode = True


class UpdateToken(BaseModel):
    data: str
