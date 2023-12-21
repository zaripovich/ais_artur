import json
import os
import random
import string
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from fastapi.testclient import TestClient
from models.book import Book
from models.user import User
from models.post import Post
from routes.books import init_books_routes
from routes.posts import init_posts_routes
from routes.users import init_users_routes
from routes.auth import init_auth_routes


dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app.add_middleware(SQLAlchemyMiddleware, db_url=os.environ["DATABASE_URL"])

init_books_routes(app, oauth2_scheme)
init_posts_routes(app, oauth2_scheme)
init_users_routes(app, oauth2_scheme)
init_auth_routes(app)

client = TestClient(app)
auth = ""


test_book = Book(id=1, name="Book1", author="Author1")
test_user = User(id=1, username="User1", password="User1Password")
test_post = Post(
    id=1,
    title="Title1",
    book_id=test_book.id,
    user_id=test_user.id,
    text="Text for post",
)


def test_user_reg():
    test_data = {"username": test_user.username, "password": test_user.password}
    post_data = json.dumps(test_data)
    response = client.post("/reg", data=post_data)
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_login():
    data = {"username": test_user.username, "password": test_user.password}
    response = client.post("/login", data=data)
    print(response.json())
    assert "access_token" in response.json()
    global auth
    auth = response.json()["access_token"]


def test_user_get_by_id():
    response = client.get(
        f"/users/get/id/{test_user.id}", headers={"Authorization": f"Bearer {auth}"}
    )
    print(response.json())
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_user_get_by_username():
    response = client.get(
        f"/users/get/username/{test_user.username}",
        headers={"Authorization": f"Bearer {auth}"},
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_book_add():
    test_data = {"name": test_book.name, "author": test_book.author}
    post_data = json.dumps(test_data)
    response = client.post(
        "/books/add", data=post_data, headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] == 1


def test_book_get_by_id():
    response = client.get(
        f"/books/get/id/{test_book.id}", headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_book_get_by_name():
    response = client.get(
        f"/books/get/name/{test_book.name}", headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_post_add():
    test_data = {
        "user_id": test_post.user_id,
        "book_id": test_post.book_id,
        "text": test_post.text,
        "title": test_post.title,
    }
    post_data = json.dumps(test_data)
    response = client.post(
        "/posts/add", data=post_data, headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] == 1


def test_post_get_by_id():
    response = client.get(
        f"/posts/get/id/{test_post.id}", headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_post_get_by_username():
    response = client.get(
        f"/posts/get/username/{test_user.username}",
        headers={"Authorization": f"Bearer {auth}"},
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_post_get_by_title():
    response = client.get(
        f"/posts/get/title/{test_post.title}",
        headers={"Authorization": f"Bearer {auth}"},
    )
    assert response.json()["code"] == 200
    assert response.json()["value"] != None


def test_post_get_by_page():
    response = client.get(
        f"/posts/get/page/1", headers={"Authorization": f"Bearer {auth}"}
    )
    assert response.json()["code"] == 200
