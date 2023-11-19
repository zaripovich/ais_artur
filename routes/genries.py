from fastapi import FastAPI
import pydantic
from typing import Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db import get_session
from models.genre import Genre, GenreSchema
from typing import Optional


class NewGenre(BaseModel):
    name: str


class DeleteResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[bool] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[bool] = True,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[int] = 1,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class GenreResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[GenreSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[GenreSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class GenriesResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[list[GenreSchema]] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[list[GenreSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init(app: FastAPI):
    @app.post("/genries/add", response_model=AddResponse)
    async def add(data: NewGenre, session: AsyncSession = Depends(get_session)) -> Any:
        try:
            new_genre = Genre()
            new_genre.name = data.name
            result = await new_genre.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/genries/get/id/{id}", response_model=GenreResponse)
    async def get_by_id(id: int, session: AsyncSession = Depends(get_session)) -> Any:
        try:
            result = await Genre.get_by_id(session, id)
            if result.is_error is True:
                return GenreResponse(code=500, error_desc=result.error_desc)
            return GenreResponse(code=200, value=Genre.from_one_to_schema(result.value))
        except Exception as e:
            return GenreResponse(code=500, error_desc=str(e))

    @app.get("/genries/get/name/{name}", response_model=GenreResponse)
    async def get_by_name(
        name: str, session: AsyncSession = Depends(get_session)
    ) -> Any:
        try:
            result = await Genre.get_by_name(session, name)
            if result.is_error is True:
                return GenreResponse(code=500, error_desc=result.error_desc)
            return GenreResponse(code=200, value=Genre.from_one_to_schema(result.value))
        except Exception as e:
            return GenriesResponse(code=500, error_desc=str(e))

    @app.delete("/genries/delete/{id}", response_model=DeleteResponse)
    async def delete(id: int, session: AsyncSession = Depends(get_session)) -> Any:
        try:
            result = await Genre.delete(session, id)
            if result.is_error is True:
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(code=200, value=result.value)
        except Exception as e:
            return DeleteResponse(code=500, error_desc=str(e))
