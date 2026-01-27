import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting hello_world...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
