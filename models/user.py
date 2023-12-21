from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, delete, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from db import Base, DbResult


class UserSchema(BaseModel):
    id: int = Field(exclude=False, title="id")
    username: str = Field(exclude=False, title="username")
    password: str = Field(exclude=False, title="password")


# pylint: disable=E0213,C0115,C0116,W0718
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String, unique=False)

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

    async def get_by_id(session: AsyncSession, user_id: int) -> DbResult:
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def get_by_username(session: AsyncSession, user_name: str) -> DbResult:
        try:
            result = await session.execute(
                select(User).where(User.username == user_name)
            )
            data = result.scalars().first()
            await session.commit()
            return DbResult.result(data)
        except Exception as e:
            return DbResult.error(str(e))

    async def delete(session: AsyncSession, user_id: int) -> DbResult:
        try:
            _ = await session.execute(delete(User).where(User.id == user_id))
            await session.commit()
            return DbResult.result(True)
        except Exception as e:
            await session.rollback()
            return DbResult.error(str(e), False)

    def from_one_to_schema(user: User) -> UserSchema:
        try:
            user_schema = UserSchema(
                id=user.id, username=user.username, password=user.password
            )
            return user_schema
        except Exception as e:
            print(e)
            return None

    def from_list_to_schema(users: List[User]) -> list[UserSchema]:
        try:
            return [User.from_one_to_schema(g) for g in users]
        except Exception:
            return []


async def init_user(engine: AsyncEngine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
