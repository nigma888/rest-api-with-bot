from .models import Tag, Article, User, Category, article_category, article_tag
from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException
from .database import get_session
from api.routers.websockets import manager
from api import schemas

import datetime
import secrets
import os
import json
import websockets
from config import Config
import datetime
import asyncio


def create_category(data, session: Session):
    category = Category(name=data["name"])
    session.add(category)
    session.commit()
    return category


def create_tag(data, session: Session):
    tag = Tag(name=data["name"])
    session.add(tag)
    session.commit()
    return tag


def get_all_category(session: Session):
    items = session.query(Category).all()
    return items


def get_all_tag(session: Session):
    items = session.query(Tag).all()
    return items


def get_all_article(
    session: Session,
    per_page: int = None,
    page: int = None,
    tags_ids=None,
    categories_ids=None,
    performers_ids=None,
    contragents_ids=None,
    contragents_names=None,
):
    # def q(filter, page=0, page_size=None):
    # query = session.query(...).filter(filter)
    # if page_size:
    #     query = query.limit(page_size)
    # if page:
    #     query = query.offset(page*page_size)
    # return query
    # items = (
    #     session.query(Article)
    #     .join(Article.category)
    #     .join(Article.tags)
    #     .filter(
    #         or_(article_tag.columns.tag_id.in_(tags_ids), not tags_ids),
    #         or_(
    #             article_category.columns.category_id.in_(categories_ids),
    #             not categories_ids,
    #         ),
    #         or_(Article.performer_id.in_(performers_ids), not performers_ids),
    #         or_(Article.client_tablecrm_id.in_(contragents_ids), not contragents_ids),
    #         or_(
    #             Article.client_tablecrm.in_(contragents_names),
    #             not contragents_names,
    #         ),
    #     )
    #     .order_by(Article.time_updated.desc())
    #     .all()
    # )
    if per_page:
        items = (
            session.query(Article)
            .filter(
                or_(article_tag.columns.tag_id.in_(tags_ids), not tags_ids),
                or_(
                    article_category.columns.category_id.in_(categories_ids),
                    not categories_ids,
                ),
                or_(Article.performer_id.in_(performers_ids), not performers_ids),
                or_(
                    Article.client_tablecrm_id.in_(contragents_ids), not contragents_ids
                ),
                or_(
                    Article.client_tablecrm.in_(contragents_names),
                    not contragents_names,
                ),
            )
            .limit(per_page)
            .offset(page * per_page)
            .all()
        )
    else:
        items = (
            session.query(Article)
            .filter(
                or_(article_tag.columns.tag_id.in_(tags_ids), not tags_ids),
                or_(
                    article_category.columns.category_id.in_(categories_ids),
                    not categories_ids,
                ),
                or_(Article.performer_id.in_(performers_ids), not performers_ids),
                or_(
                    Article.client_tablecrm_id.in_(contragents_ids), not contragents_ids
                ),
                or_(
                    Article.client_tablecrm.in_(contragents_names),
                    not contragents_names,
                ),
            )
            .limit(per_page)
            .all()
        )

    return items


def get_article_by_id(id, session: Session):
    return session.query(Article).get(id)


async def create_article(data, main, header, session: Session):

    tags = session.query(Tag).filter(Tag.id.in_(data["tags"])).all()
    data["tags"] = tags

    user = session.query(User).get(data["owner"])
    data["owner"] = user

    category = session.query(Category).filter(Category.id.in_(data["category"])).all()
    data["category"] = category

    performer = session.query(User).get(data["performer"])
    data["performer"] = performer

    article = Article(**data)
    session.add(article)
    session.commit()

    if header:
        article.header_pic = f"images/header_pic/{article.id}.{header}"
    if main:
        article.main_pic = f"images/main_pic/{article.id}.{main}"

    session.add(article)
    session.commit()

    await manager.broadcast(
        json.dumps(
            {
                "type": "CreateArticle",
                "id": article.id,
                "TimeStamp": str(datetime.datetime.now()),
            }
        )
    )

    return article


async def update_article(data, main, header, session: Session):
    article = session.query(Article).get(data["id"])

    if article:

        tags = (
            session.query(Tag).filter(Tag.id.in_(data["tags"])).all()
            if data["tags"]
            else article.tags
        )
        category = (
            session.query(Category).filter(Category.id.in_(data["category"])).all()
            if data["category"]
            else article.category
        )
        performer = (
            session.query(User).get(data["performer"])
            if data["performer"]
            else article.performer
        )

        del data["tags"]
        del data["category"]
        del data["performer"]

        for key, value in data.items():
            if value:
                setattr(article, key, value)

        if header:
            if article.header_pic:
                os.remove(article.header_pic)
            article.header_pic = f"images/header_pic/{article.id}.{header}"
        if main:
            if article.main_pic:
                os.remove(article.main_pic)
            article.main_pic = f"images/main_pic/{article.id}.{main}"

        article.tags = tags

        article.category = category
        article.performer = performer

        # article.title = data["title"]
        # article.first_sentence = data["first_sentence"]
        # article.content = data["content"]

        # article.price_hour = data["price_hour"]
        # article.client_tablecrm = data["client_tablecrm"]
        # article.client_tablecrm_id = data["client_tablecrm_id"]
        # article.project_tablecrm = data["project_tablecrm"]
        # article.project_tablecrm_id = data["project_tablecrm_id"]
        # article.seo_url = data["seo_url"]

        session.commit()

        await manager.broadcast(
            json.dumps(
                {
                    "type": "UpdateArticle",
                    "id": article.id,
                    "TimeStamp": str(datetime.datetime.now()),
                }
            )
        )

    else:
        raise HTTPException(404)
    return article


async def create_user(id, name, profile_pic, url_ws):
    session = next(get_session())
    user = session.query(User).filter(User.tg_id == id).first()
    flag = False
    if not user:
        flag = True
        token = secrets.token_hex(16)
        while session.query(User).filter(User.token == token).first():
            token = secrets.token_hex(16)
        user = User(tg_id=id, name=name, token=token, profile_pic=profile_pic)
        session.add(user)
    else:
        token = secrets.token_hex(16)
        while session.query(User).filter(User.token == token).first():
            token = secrets.token_hex(16)
        user.token = token
        user.name = name
        user.profile_pic = profile_pic

    session.commit()
    session.refresh(user)

    if flag:
        await send_wb(url_ws, id)
    return user


async def send_wb(url, id):
    async with websockets.connect(url) as websocket:
        await websocket.send(
            Config.SECRET_TOKEN_WS + ";" + str(id) + ";" + str(datetime.datetime.now())
        )
        websocket.close()


async def update_user(data, profile_pic, session: Session):

    user = session.query(User).get(data["id"])
    flag = True if user.role != data["role"] else False
    if user:

        for key, value in data.items():
            if value:
                setattr(user, key, value)
        if profile_pic and user.profile_pic:
            os.remove(user.profile_pic)

        if profile_pic:
            user.profile_pic = f"images/profile_pic/{user.tg_id}.{profile_pic}"

        session.commit()

        # user.name = data["name"]
        # user.role = data["role"]

        # user.profile_pic = f"images/profile_pic/{user.tg_id}.{profile_pic}"

        if flag:
            await manager.broadcast(
                json.dumps(
                    {
                        "type": "UpdateUserPermission",
                        "id": user.id,
                        "TimeStamp": str(datetime.datetime.now()),
                    }
                )
            )

    else:
        raise HTTPException(404)
    return user


def get_user_by_token(token, session: Session):
    user = session.query(User).filter(User.token == token).first()
    if not user:
        return None
    return user


def get_all_users(session: Session):
    items = session.query(User).all()
    return items
