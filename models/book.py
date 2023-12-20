from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import Column, ForeignKey, Integer, String, delete, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import mapped_column

from db import Base, DbResult


class BookSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    name: str = Field(exclude=False, title="name")
    author: str = Field(exclude=False, title="author")


# pylint: disable=E0213,C0115,C0116,W0718
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)
    author = Column(String)

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    async def get_by_id(session: AsyncSession, book_id: int) -> DbResult:
        try:
            result = await session.execute(select(Book).where(Book.id == book_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_name(session: AsyncSession, book_name: int) -> DbResult:
        try:
            result = await session.execute(select(Book).where(Book.name == book_name))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def delete(session: AsyncSession, book_id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Book).where(Book.id == book_id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    def from_one_to_schema(book: Book) -> BookSchema:
        try:
            book_schema = BookSchema(
                id=book.id,
                name=book.name,
                author=book.author,
            )
            return book_schema
        except Exception:
            return None

    def from_list_to_schema(books: List[Book]) -> list[BookSchema]:
        try:
            return [Book.from_one_to_schema(b) for b in books]
        except Exception:
            return []


async def init_book(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
