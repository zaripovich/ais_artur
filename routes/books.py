from typing import Annotated, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.book import Book, BookSchema
from models.user import User
from routes.auth import get_current_user


class NewBook(BaseModel):
    name: str = Field()
    author: str = Field()


# pylint: disable=E0213,C0115,C0116,W0718
class DeleteResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[bool] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[bool] = True,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self, code: int = 200, error_desc: Optional[str] = "", value: Optional[int] = 1
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class BookResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[BookSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[BookSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


# pylint: disable=E0213,C0115,C0116,W0718
class BooksResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[BookSchema]] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[BookSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init(app: FastAPI, oauth2_scheme):
    @app.post(
        "/books/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        user: Annotated[str, Depends(oauth2_scheme)],
        data: NewBook,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            new_book = Book()
            new_book.name = data.name
            new_book.author = data.author
            result = await new_book.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get(
        "/books/get/id/{id}",
        response_model=BookResponse,
        response_model_exclude_none=True,
    )
    async def get_by_id(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Book.get_by_id(session, id)
            if result.is_error is True:
                return BookResponse(code=500, error_desc=result.error_desc)
            return BookResponse(code=200, value=Book.from_one_to_schema(result.value))
        except Exception as e:
            return BookResponse(code=500, error_desc=str(e))

    @app.get(
        "/books/get/genre/{genre}",
        response_model=BooksResponse,
        response_model_exclude_none=True,
    )
    async def get_by_genre(
        current_user: Annotated[User, Depends(get_current_user)],
        genre: str,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Book.get_by_genre(session, genre)
            if result.is_error is True:
                return BooksResponse(code=500, error_desc=result.error_desc)
            return BooksResponse(code=200, value=Book.from_list_to_schema(result.value))
        except Exception as e:
            return BooksResponse(code=500, error_desc=str(e))

    @app.get(
        "/books/get/name/{name}",
        response_model=BookResponse,
        response_model_exclude_none=True,
    )
    async def get_by_name(
        current_user: Annotated[User, Depends(get_current_user)],
        name: str,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Book.get_by_name(session, name)
            if result.is_error is True:
                return BookResponse(code=500, error_desc=result.error_desc)
            return BookResponse(code=200, value=Book.from_one_to_schema(result.value))
        except Exception as e:
            return BookResponse(code=500, error_desc=str(e))

    @app.delete(
        "/books/delete/{id}",
        response_model=DeleteResponse,
        response_model_exclude_none=True,
    )
    async def delete(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result = await Book.delete(session, id)
            if result is False:
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(code=200, value=result.value)
        except Exception as e:
            return DeleteResponse(code=500, error_desc=str(e))
