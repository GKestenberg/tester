import logging
import os
import subprocess
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)


def detect_gpu() -> bool:
    """Detect if the node has GPU available."""
    # Check for NVIDIA GPU environment variables
    if os.environ.get("NVIDIA_VISIBLE_DEVICES") or os.environ.get("CUDA_VISIBLE_DEVICES"):
        return True

    # Try nvidia-smi command
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try importing torch and checking CUDA
    try:
        import torch
        if torch.cuda.is_available():
            return True
    except ImportError:
        pass

    return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    has_gpu = detect_gpu()
    node_type = "GPU" if has_gpu else "CPU"
    print(f"Starting hello_gpu on {node_type} node...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "hello gpu"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
