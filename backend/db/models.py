from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Enum,
    Text,
    Table,
    BigInteger,
    Float,
    Numeric,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base
from externals.userRole import UserRole

article_tag = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

article_category = Table(
    "article_category",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True),
)


class File(Base):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    hash = Column(String)
    link = Column(String)
    type = Column(String)
    file_size = Column(Float)
    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    tg_id = Column(BigInteger)
    name = Column(String)
    token = Column(String, index=True)

    role = Column(Enum(UserRole), default="MANAGER")
    profile_pic = Column(String, nullable=True)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isPublic = Column(Boolean, default=False)
    isPublish = Column(Boolean, default=False)
    title = Column(String, nullable=True)
    first_sentence = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    price_hour = Column(Float, nullable=True)

    client_tablecrm = Column(Text, nullable=True, default=None)
    client_tablecrm_id = Column(Numeric, nullable=True)

    seo_url = Column(String, nullable=True)

    project_tablecrm = Column(Text, nullable=True, default=None)
    project_tablecrm_id = Column(Numeric, nullable=True)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True))

    performer_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)

    owner_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    header_pic = Column(String, nullable=True)
    main_pic = Column(String, nullable=True)

    category = relationship("Category", secondary=article_category, backref="articles")

    tags = relationship("Tag", secondary=article_tag, backref="articles")

    performer = relationship("User", backref="performs", foreign_keys=[performer_id])

    owner = relationship("User", backref="articles", foreign_keys=[owner_id])

    __mapper_args__ = {"eager_defaults": True}


class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
