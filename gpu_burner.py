#!/usr/bin/env python3
"""
GPU Burner - FastAPI app that can allocate/release VRAM for testing.
Uses raw CUDA API via ctypes - no additional packages needed.
"""

import ctypes
from fastapi import FastAPI

app = FastAPI(title="GPU Burner")

# Global reference to hold GPU memory pointers
gpu_allocations = []
cuda = None


def get_cuda():
    """Load CUDA runtime library."""
    global cuda
    if cuda is not None:
        return cuda

    try:
        # Try common CUDA library paths
        for lib_name in ['libcudart.so', 'libcudart.so.12', 'libcudart.so.11', 'cudart64_12.dll', 'cudart64_11.dll']:
            try:
                cuda = ctypes.CDLL(lib_name)
                return cuda
            except OSError:
                continue
        return None
    except Exception:
        return None


@app.get("/")
async def hello():
    return {"message": "Hello GPU Burner!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/load")
async def load():
    """Allocate ~2GB of VRAM."""
    global gpu_allocations

    cuda = get_cuda()
    if cuda is None:
        return {"status": "error", "message": "CUDA runtime not available"}

    try:
        # Clear existing allocations
        for ptr in gpu_allocations:
            cuda.cudaFree(ptr)
        gpu_allocations.clear()

        # Allocate 2GB
        size = 2 * 1024 * 1024 * 1024  # 2GB in bytes
        ptr = ctypes.c_void_p()

        result = cuda.cudaMalloc(ctypes.byref(ptr), ctypes.c_size_t(size))

        if result != 0:
            return {"status": "error", "message": f"cudaMalloc failed with error {result}"}

        gpu_allocations.append(ptr)

        # Get memory info
        free = ctypes.c_size_t()
        total = ctypes.c_size_t()
        cuda.cudaMemGetInfo(ctypes.byref(free), ctypes.byref(total))

        return {
            "status": "loaded",
            "allocated_mb": 2048,
            "free_mb": round(free.value / (1024 * 1024), 2),
            "total_mb": round(total.value / (1024 * 1024), 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/reset")
async def reset():
    """Release allocated VRAM."""
    global gpu_allocations

    cuda = get_cuda()
    if cuda is None:
        return {"status": "error", "message": "CUDA runtime not available"}

    try:
        for ptr in gpu_allocations:
            cuda.cudaFree(ptr)
        gpu_allocations.clear()

        # Get memory info
        free = ctypes.c_size_t()
        total = ctypes.c_size_t()
        cuda.cudaMemGetInfo(ctypes.byref(free), ctypes.byref(total))

        return {
            "status": "reset",
            "free_mb": round(free.value / (1024 * 1024), 2),
            "total_mb": round(total.value / (1024 * 1024), 2)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/status")
async def status():
    """Get current GPU memory status."""
    cuda = get_cuda()
    if cuda is None:
        return {"status": "error", "message": "CUDA runtime not available"}

    try:
        free = ctypes.c_size_t()
        total = ctypes.c_size_t()
        cuda.cudaMemGetInfo(ctypes.byref(free), ctypes.byref(total))

        return {
            "cuda_available": True,
            "free_mb": round(free.value / (1024 * 1024), 2),
            "total_mb": round(total.value / (1024 * 1024), 2),
            "used_mb": round((total.value - free.value) / (1024 * 1024), 2),
            "allocations_held": len(gpu_allocations)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
