from typing import Annotated, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import DbResult, get_session
from models.post import Post, PostSchema
from models.user import User
from routes.auth import get_current_user


class NewPost(BaseModel):
    user_id: int
    title: str
    text: str
    book_name: str
    book_author: str


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


class AddResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[int] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[int] = 0,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class PostResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[PostSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[PostSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class PostsResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[PostSchema]] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[PostSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init_posts_routes(app: FastAPI, oauth2_scheme):
    @app.post(
        "/posts/add", response_model=AddResponse, response_model_exclude_none=True
    )
    async def add(
        current_user: Annotated[User, Depends(get_current_user)],
        data: NewPost,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            user = await User.get_by_id(session, data.user_id)
            if user.is_error:
                raise Exception("User with this user_id not found")
            new_post = Post()
            new_post.title = data.title
            new_post.user_id = user.value.id
            new_post.text = data.text
            new_post.book_name = data.book_name
            new_post.book_author = data.book_author
            result = await new_post.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/posts/get/page/{page}", response_model=PostsResponse)
    async def get_by_page(
        current_user: Annotated[User, Depends(get_current_user)],
        page: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Post.get_by_page(session, page)
            if result.is_error is True:
                return PostsResponse(code=500, error_desc=result.error_desc)
            return PostsResponse(
                code=200, value=await Post.from_list_to_schema(session, result.value)
            )
        except Exception as e:
            return PostsResponse(code=500, error_desc=str(e))
    

    @app.get("/posts/get/all", response_model=PostsResponse)
    async def get_by_page(
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Post.get_all(session)
            if result.is_error is True:
                return PostsResponse(code=500, error_desc=result.error_desc)
            return PostsResponse(
                code=200, value=await Post.from_list_to_schema(session, result.value)
            )
        except Exception as e:
            return PostsResponse(code=500, error_desc=str(e))

    @app.get("/posts/get/id/{id}", response_model=PostResponse)
    async def get_by_id(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Post.get_by_id(session, id)
            if result.is_error is True:
                return PostResponse(code=500, error_desc=result.error_desc)
            return PostResponse(
                code=200, value=await Post.from_one_to_schema(session, result.value)
            )
        except Exception as e:
            return PostResponse(code=500, error_desc=str(e))

    @app.get("/posts/get/username/{username}", response_model=PostsResponse)
    async def get_by_username(
        current_user: Annotated[User, Depends(get_current_user)],
        username: str,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Post.get_by_username(session, username)
            if result.is_error is True:
                return PostsResponse(code=500, error_desc=result.error_desc)
            return PostsResponse(
                code=200, value=await Post.from_list_to_schema(session, result.value)
            )
        except Exception as e:
            return PostsResponse(code=500, error_desc=str(e))

    @app.get("/posts/get/title/{title}", response_model=PostsResponse)
    async def get_by_title(
        current_user: Annotated[User, Depends(get_current_user)],
        title: str,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result: DbResult = await Post.get_by_title(session, title)
            if result.is_error is True:
                return PostsResponse(code=500, error_desc=result.error_desc)
            return PostsResponse(
                code=200, value=await Post.from_list_to_schema(session, result.value)
            )
        except Exception as e:
            return PostsResponse(code=500, error_desc=str(e))

    @app.delete("/posts/delete/{id}", response_model=DeleteResponse)
    async def delete(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ):
        try:
            result = await Post.delete(session, id)
            if result is False:
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(200, value=result.value)
        except Exception as e:
            return DeleteResponse(code=500, error_desc=str(e))
