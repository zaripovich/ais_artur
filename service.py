import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

from db import engine
from models.book import init_book
from models.post import init_post
from models.user import init_user

# pylint: disable=E0401
from routes.auth import init_auth_routes
from routes.books import init_books_routes
from routes.posts import init_posts_routes
from routes.users import init_users_routes

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)




app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Custom title",
        version="2.5.0",
        summary="This is a very custom OpenAPI schema",
        description="Here's a longer description of the custom **OpenAPI** schema",
        routes=app.routes,
    )
    return openapi_schema


async def init_models():
    try:
        if os.environ.get("REINIT_DB") == "1":
            await init_book(engine)
            await init_user(engine)
            await init_post(engine)
        print("Done")
    except Exception as e:
        print(e)


def run():
    init_books_routes(app, oauth2_scheme)
    init_posts_routes(app, oauth2_scheme)
    init_users_routes(app, oauth2_scheme)
    init_auth_routes(app)
    app.openapi_schema = custom_openapi()
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
