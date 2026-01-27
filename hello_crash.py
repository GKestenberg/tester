import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting hello_crash...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "hello crash!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


def kill_server():
    os._exit(1)


@app.get("/crash")
def crash(background_tasks: BackgroundTasks):
    background_tasks.add_task(kill_server)
    return {"message": "goodbye"}
