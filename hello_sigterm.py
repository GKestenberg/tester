import logging
import signal
import sys
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)

sigterm_received = False
sigterm_time: float = 0.0


def sigterm_handler(signum, frame):
    global sigterm_received, sigterm_time
    sigterm_received = True
    sigterm_time = time.time()
    print("SIGTERM received!", flush=True)


def sigterm_timer():
    global sigterm_received, sigterm_time
    while True:
        if sigterm_received:
            elapsed = int(time.time() - sigterm_time)
            print(f"time since sigterm... {elapsed}s", flush=True)
        time.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    signal.signal(signal.SIGTERM, sigterm_handler)
    timer_thread = threading.Thread(target=sigterm_timer, daemon=True)
    timer_thread.start()
    print("Starting hello_sigterm...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "hello sigterm!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
