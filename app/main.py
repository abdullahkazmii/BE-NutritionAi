from dotenv import load_dotenv
from fastapi import FastAPI

from .database import engine, Base

load_dotenv()
app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}
