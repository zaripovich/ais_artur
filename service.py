import os
from fastapi import FastAPI
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
import uvicorn
from fastapi.openapi.utils import get_openapi

# pylint: disable=E0401
from routes import books, genries, reviews

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
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
    books.init(app)
    genries.init(app)
    reviews.init(app)
    app.openapi_schema = custom_openapi()
    uvicorn.run(app, host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))
