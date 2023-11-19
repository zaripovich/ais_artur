from __future__ import annotations
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy.orm import mapped_column
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from db import Base, DbResult
from pydantic import BaseModel, Field


class BookSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    name: str = Field(exclude=False, title="name")
    description: str = Field(exclude=False, title="description")
    genre_id: int = Field(exclude=False, title="genre_id")


# pylint: disable=E0213,C0115,C0116,W0718
class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    genre_id = mapped_column(ForeignKey("genries.id"))

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

    async def get_by_genre(session: AsyncSession, genre: int) -> DbResult:
        try:
            result = await session.execute(select(Book).where(Book.genre_id == genre))
            data = result.scalars().all()
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
                description=book.description,
                genre_id=book.genre_id,
            )
            return book_schema
        except Exception:
            return None

    def from_list_to_schema(books: [Book]) -> list[BookSchema]:
        try:
            return [Book.from_one_to_schema(b) for b in books]
        except Exception:
            return []


async def init_book(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)