import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware

# pylint: disable=E0401
from routes import auth, books, genries, reviews, users

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
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


def run():
    books.init(app,oauth2_scheme)
    genries.init(app,oauth2_scheme)
    reviews.init(app,oauth2_scheme)
    users.init(app,oauth2_scheme)
    auth.init(app)
    app.openapi_schema = custom_openapi()
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
