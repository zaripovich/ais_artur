from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import Column, ForeignKey, Integer, String, delete, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import mapped_column

from db import Base, DbResult
from models.user import User


class PostSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    username: str = Field(exclude=False, title="username")
    title: str = Field(exclude=False, title="title")
    text: str = Field(exclude=False, title="text")
    book_name: str = Field(exclude=False, title="book_name")
    book_author: str = Field(exclude=False, title="book_name")


# pylint: disable=E0213,C0115,C0116,W0718
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String)
    text = Column(String)
    book_name = Column(String)
    book_author = Column(String)
    user_id = mapped_column(ForeignKey("users.id"))

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(e)

    async def get_by_id(session: AsyncSession, post_id: int) -> DbResult:
        try:
            result = await session.execute(select(Post).where(Post.id == post_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_page(session: AsyncSession, page: int) -> DbResult:
        try:
            result = await session.execute(
                select(Post).offset(10 * (page - 1)).limit(10)
            )
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))
    
    async def get_all(session: AsyncSession) -> DbResult:
        try:
            result = await session.execute(
                select(Post)
            )
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_username(session: AsyncSession, _username: String) -> DbResult:
        try:
            result = await session.execute(
                select(Post).where(
                    Post.user_id == select(User.id).where(User.username == _username)
                )
            )
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_title(session: AsyncSession, _title: String) -> DbResult:
        try:
            result = await session.execute(select(Post).where(Post.title == _title))
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def delete(session: AsyncSession, post_id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Post).where(Post.id == post_id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    async def from_one_to_schema(session: AsyncSession, post: Post) -> PostSchema:
        try:
            user = await User.get_by_id(session, post.user_id)
            if not user.is_error:
                post_schema = PostSchema(
                    id=post.id,
                    title=post.title,
                    username=user.value.username,
                    text=post.text,
                    book_name=post.book_name,
                    book_author=post.book_author,
                )
                return post_schema
            return None
        except Exception:
            return None

    async def from_list_to_schema(session, posts: List[Post]) -> list[PostSchema]:
        try:
            return [await Post.from_one_to_schema(session, r) for r in posts]
        except Exception:
            return []


async def init_post(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
