from __future__ import annotations
from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from db import Base, DbResult
from pydantic import BaseModel, Field


class GenreSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    name: str = Field(exclude=False, title="name")


# pylint: disable=E0213,C0115,C0116,W0718
class Genre(Base):
    __tablename__ = "genries"

    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String, unique=True)

    async def add(self, session: AsyncSession) -> DbResult:
        try:
            copy = self
            session.add(copy)
            await session.commit()
            await session.refresh(copy)
            return DbResult.result(copy.id)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e))

    async def get_by_id(session: AsyncSession, genre_id: int) -> DbResult:
        try:
            result = await session.execute(select(Genre).where(Genre.id == genre_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_name(session: AsyncSession, genre_name: int) -> DbResult:
        try:
            result = await session.execute(
                select(Genre).where(Genre.name == genre_name)
            )
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def delete(session: AsyncSession, genre_id: int) -> DbResult:
        try:
            _ = await session.execute(delete(Genre).where(Genre.id == genre_id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    def from_one_to_schema(genre: Genre) -> GenreSchema:
        try:
            genre_schema = GenreSchema(id=genre.id, name=genre.name)
            return genre_schema
        except Exception as e:
            print(e)
            return None

    def from_list_to_schema(genries: [Genre]) -> list[GenreSchema]:
        try:
            return [Genre.from_one_to_schema(g) for g in genries]
        except Exception:
            return []


async def init_genre(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
