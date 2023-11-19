from fastapi import FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db import get_session, DbResult
from models.review import Review, ReviewSchema
from typing import Optional


class NewReview(BaseModel):
    username: str
    text: str
    book_id: int


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
        value: Optional[int] = 0,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class ReviewResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[ReviewSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[ReviewSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class ReviewsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: str = Field(exclude=False, title="description")
    value: Optional[list[ReviewSchema]] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: str = "",
        value: Optional[list[ReviewSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init(app: FastAPI):
    @app.post("/reviews/add", response_model=AddResponse)
    async def add(data: NewReview, session: AsyncSession = Depends(get_session)):
        try:
            new_review = Review()
            new_review.username = data.username
            new_review.text = data.text
            new_review.book_id = data.book_id
            result = await new_review.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/reviews/get/id/{id}", response_model=ReviewResponse)
    async def get_by_id(id: int, session: AsyncSession = Depends(get_session)):
        try:
            result: DbResult = await Review.get_by_id(session, id)
            if result.is_error is True:
                return ReviewResponse(code=500, error_desc=result.error_desc)
            return ReviewResponse(
                code=200, value=Review.from_one_to_schema(result.value)
            )
        except Exception as e:
            return ReviewResponse(code=500, error_desc=str(e))

    @app.get("/reviews/get/username/{name}", response_model=ReviewsResponse)
    async def get_by_username(
        username: str, session: AsyncSession = Depends(get_session)
    ):
        try:
            result: DbResult = await Review.get_by_username(session, username)
            if result.is_error is True:
                return ReviewsResponse(code=500, error_desc=result.error_desc)
            return ReviewsResponse(
                code=200, value=Review.from_list_to_schema(result.value)
            )
        except Exception as e:
            return ReviewsResponse(code=500, error_desc=str(e))

    @app.delete("/reviews/delete/{id}", response_model=DeleteResponse)
    async def delete(id: int, session: AsyncSession = Depends(get_session)):
        try:
            result = await Review.delete(session, id)
            if result is False:
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(200, value=result.value)
        except Exception as e:
            return DeleteResponse(code=500, error_desc=str(e))
