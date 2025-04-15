from dotenv import load_dotenv
from fastapi import FastAPI
from .database import engine, Base
from .models import User
from passlib.hash import bcrypt
from sqlalchemy import event
from app.user import user
from app.user import router as user_router

load_dotenv()

INITIAL_DATA = {
    "users": [
        {
            "id": 1,
            "name": "admin",
            "username": "admin",
            "email": "admin@example.com",
            "password": bcrypt.hash("admin123"),
            "role": "admin",
        }
    ]
}


def initialize_table(target, connection, **kw):
    tablename = str(target)
    if tablename == "users" and len(INITIAL_DATA["users"]) > 0:
        connection.execute(target.insert(), INITIAL_DATA["users"])


event.listen(User.__table__, "after_create", initialize_table)

app = FastAPI()

# import user router
app.include_router(user_router, tags=["user"])


@app.get("/health")
async def health():
    return {"status": "ok"}


