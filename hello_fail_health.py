import logging
import sys
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

health_checked = False
health_check_time: float = 0.0


def health_timer():
    global health_checked, health_check_time
    while True:
        if health_checked:
            elapsed = int(time.time() - health_check_time)
            print(f"hello_fail_health... {elapsed}s", flush=True)
        time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    timer_thread = threading.Thread(target=health_timer, daemon=True)
    timer_thread.start()
    print("Starting hello_fail_health...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "hello fail health!"}


@app.get("/health")
def health_check():
    global health_checked, health_check_time
    if not health_checked:
        health_checked = True
        health_check_time = time.time()
    return JSONResponse(status_code=503, content={"status": "unhealthy"})
