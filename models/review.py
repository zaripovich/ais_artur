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


class ReviewSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    username: str = Field(exclude=False, title="username")
    text: str = Field(exclude=False, title="text")
    book_id: int = Field(exclude=False, title="book_id")


# pylint: disable=E0213,C0115,C0116,W0718
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String)
    text = Column(String)
    book_id = mapped_column(ForeignKey("books.id"))

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return DbResult.result(self.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(e)

    async def get_by_id(session: AsyncSession, review_id: int) -> DbResult:
        try:
            result = await session.execute(select(Review).where(Review.id == review_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_username(session: AsyncSession, _username: String) -> DbResult:
        try:
            result = await session.execute(
                select(Review).where(Review.username == _username)
            )
            data = result.scalars().all()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def delete(session: AsyncSession, review_id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Review).where(Review.id == review_id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    def from_one_to_schema(review: Review) -> ReviewSchema:
        try:
            review_schema = ReviewSchema(
                id=review.id,
                username=review.username,
                text=review.text,
                book_id=review.book_id,
            )
            return review_schema
        except Exception:
            return None

    def from_list_to_schema(reviews: [Review]) -> list[ReviewSchema]:
        try:
            return [Review.from_one_to_schema(r) for r in reviews]
        except Exception:
            return []


async def init_review(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
