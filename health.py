#!/usr/bin/env python3
"""
Health Check Demo - FastAPI app demonstrating startup, liveness, and readiness probes.
"""

import asyncio
from fastapi import FastAPI, Response

app = FastAPI(title="Health Check Demo")

# State tracking
startup_complete = False
startup_requested = False
liveness_healthy = True
readiness_healthy = True
startup_task = None
liveness_task = None
readiness_task = None


async def count_up(prefix: str, state_name: str):
    """Print counting message every second."""
    counter = 1
    while True:
        print(f"{prefix}... {counter}s", flush=True)
        counter += 1
        await asyncio.sleep(1)


@app.get("/")
async def hello():
    routes = [
        "GET  /                  - This page",
        "GET  /startup           - Startup probe (fails until second request)",
        "GET  /liveness          - Liveness probe",
        "GET  /readiness         - Readiness probe",
        "GET  /crash/liveness    - Make liveness probe fail",
        "GET  /crash/readiness   - Make readiness probe fail",
        "GET  /reset/liveness    - Restore liveness probe",
        "GET  /reset/readiness   - Restore readiness probe",
        "GET  /status            - Current health state",
    ]
    return {
        "message": "Hello Health!",
        "routes": "\n".join(routes)
    }


@app.get("/startup")
async def startup():
    """Startup probe - fails on first request, succeeds on second."""
    global startup_complete, startup_requested, startup_task

    if startup_complete:
        return Response(status_code=204)

    if not startup_requested:
        # First request - start counting and return failure
        startup_requested = True
        startup_task = asyncio.create_task(count_up("health_startup", "startup"))
        return Response(status_code=503)
    else:
        # Second request - stop counting and return success
        startup_complete = True
        if startup_task:
            startup_task.cancel()
            startup_task = None
        print("health_startup... complete", flush=True)
        return Response(status_code=204)


@app.get("/liveness")
async def liveness():
    """Liveness probe."""
    global liveness_healthy

    if liveness_healthy:
        return Response(status_code=204)
    else:
        return Response(status_code=503)


@app.get("/readiness")
async def readiness():
    """Readiness probe."""
    global readiness_healthy

    if readiness_healthy:
        return Response(status_code=204)
    else:
        return Response(status_code=503)


@app.get("/crash/liveness")
async def crash_liveness():
    """Make liveness probe fail."""
    global liveness_healthy, liveness_task

    liveness_healthy = False
    if liveness_task:
        liveness_task.cancel()
    liveness_task = asyncio.create_task(count_up("health_liveness", "liveness"))

    return {"status": "liveness probe now failing"}


@app.get("/crash/readiness")
async def crash_readiness():
    """Make readiness probe fail."""
    global readiness_healthy, readiness_task

    readiness_healthy = False
    if readiness_task:
        readiness_task.cancel()
    readiness_task = asyncio.create_task(count_up("health_readiness", "readiness"))

    return {"status": "readiness probe now failing"}


@app.get("/reset/liveness")
async def reset_liveness():
    """Restore liveness probe."""
    global liveness_healthy, liveness_task

    liveness_healthy = True
    if liveness_task:
        liveness_task.cancel()
        liveness_task = None
    print("health_liveness... restored", flush=True)

    return {"status": "liveness probe restored"}


@app.get("/reset/readiness")
async def reset_readiness():
    """Restore readiness probe."""
    global readiness_healthy, readiness_task

    readiness_healthy = True
    if readiness_task:
        readiness_task.cancel()
        readiness_task = None
    print("health_readiness... restored", flush=True)

    return {"status": "readiness probe restored"}


@app.get("/status")
async def status():
    """Get current health state."""
    return {
        "startup_complete": startup_complete,
        "startup_requested": startup_requested,
        "liveness_healthy": liveness_healthy,
        "readiness_healthy": readiness_healthy
    }
