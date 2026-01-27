#!/usr/bin/env python3
"""
Hello Metrics - Simple FastAPI app with a metrics endpoint.
"""

import time
from fastapi import FastAPI, Response

app = FastAPI(title="Hello Metrics")

# Simple in-memory counters
request_count = 0
simulated_load = 0
start_time = time.time()


@app.get("/")
async def hello():
    global request_count
    request_count += 1
    return {"message": "Hello Metrics!"}


@app.get("/load")
async def load():
    """Set simulated load to 70 requests for autoscaling testing."""
    global simulated_load
    simulated_load = 70
    return {"status": "load enabled", "simulated_requests": simulated_load}


@app.get("/reset")
async def reset():
    """Reset simulated load to 0."""
    global simulated_load
    simulated_load = 0
    return {"status": "load reset", "simulated_requests": simulated_load}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/metrics")
async def metrics():
    """Prometheus-format metrics endpoint."""
    global request_count, simulated_load
    uptime = time.time() - start_time
    total_requests = request_count + simulated_load

    # Return Prometheus text format
    metrics_text = f"""# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{endpoint="/"}} {total_requests}

# HELP app_uptime_seconds Application uptime in seconds
# TYPE app_uptime_seconds gauge
app_uptime_seconds {uptime:.2f}

# HELP app_queue_depth Current queue depth
# TYPE app_queue_depth gauge
app_queue_depth {simulated_load}
"""
    return Response(content=metrics_text, media_type="text/plain")
