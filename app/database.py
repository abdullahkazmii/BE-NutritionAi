import os
from dotenv import load_dotenv
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
for _ in range(10):
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        engine.connect()
        print("Database connected successfully")
        break
    except OperationalError:
        print("Database connection failed. Retrying...")
        time.sleep(5)
else:
    raise RuntimeError("Could not connect to the database after 10 retries.")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
