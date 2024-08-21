from fastapi import FastAPI
from pydantic import BaseModel

from app.database import users


class User(BaseModel):
    username: str


app = FastAPI()


@app.get("/")
def index():
    return "Index"


@app.post("/users")
def user_post(user: User):
    user_id = users.add_user(user.username)
    return {"id": user_id, **user.model_dump()}


@app.get("/users/{user_id}")
def user_get(user_id: int):
    return users.get_user(user_id)
