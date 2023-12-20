from typing import Annotated, Any, Optional

from fastapi import Depends, FastAPI
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session
from models.user import User, UserSchema
from routes.auth import get_current_user

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class NewUser(BaseModel):
    username: str
    password: str


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
        value: Optional[int] = 1,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class UserResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[UserSchema] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[UserSchema] = None,
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


class UsersResponse(BaseModel):
    code: int = Field(exclude=False, title="code")
    error_desc: Optional[str] = Field(exclude=False, title="description")
    value: Optional[list[UserSchema]] = Field(exclude=False, title="value")

    def __init__(
        self,
        code: int = 200,
        error_desc: Optional[str] = None,
        value: Optional[list[UserSchema]] = [],
    ):
        super().__init__(code=code, error_desc=error_desc, value=value)


def init(app: FastAPI, oauth2_scheme):
    @app.post("/reg", response_model=AddResponse)
    async def add(
        data: NewUser,
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        try:
            new_user = User()
            new_user.username = data.username
            new_user.password = pwd_context.hash(data.password)
            result = await new_user.add(session)
            if result.is_error is True:
                return AddResponse(code=500, error_desc=result.error_desc)
            return AddResponse(code=200, value=result.value)
        except Exception as e:
            return AddResponse(code=500, error_desc=str(e))

    @app.get("/users/get/id/{id}", response_model=UserResponse)
    async def get_by_id(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        try:
            result = await User.get_by_id(session, id)
            if result.is_error is True:
                return UserResponse(code=500, error_desc=result.error_desc)
            return UserResponse(code=200, value=User.from_one_to_schema(result.value))
        except Exception as e:
            return UserResponse(code=500, error_desc=str(e))

    @app.get(
        "/users/get/username/{username}",
        response_model=UserResponse,
        response_model_exclude_none=True,
    )
    async def get_by_username(
        current_user: Annotated[User, Depends(get_current_user)],
        username: str,
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        try:
            result = await User.get_by_username(session, username)
            if result.is_error is True:
                return UserResponse(code=500, error_desc=result.error_desc)
            return UserResponse(code=200, value=User.from_one_to_schema(result.value))
        except Exception as e:
            return UsersResponse(code=500, error_desc=str(e))

    @app.delete(
        "/users/delete/{id}",
        response_model=DeleteResponse,
        response_model_exclude_none=True,
    )
    async def delete(
        current_user: Annotated[User, Depends(get_current_user)],
        id: int,
        session: AsyncSession = Depends(get_session),
    ) -> Any:
        try:
            result = await User.delete(session, id)
            if result.is_error is True:
                return DeleteResponse(code=500, error_desc=result.error_desc)
            return DeleteResponse(code=200, value=result.value)
        except Exception as e:
            return DeleteResponse(code=500, error_desc=str(e))
