import logging
import sys
from contextlib import asynccontextmanager

import boto3
from fastapi import FastAPI

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting aws_iam service...", flush=True)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "hello iam, go to /list"}


@app.get("/list")
def list_roles():
    """List all IAM roles. Credentials injected via EKS Pod Identity."""
    iam = boto3.client("iam")
    roles = []
    paginator = iam.get_paginator("list_roles")
    for page in paginator.paginate():
        for role in page["Roles"]:
            roles.append({
                "name": role["RoleName"],
                "arn": role["Arn"],
            })
    return {"roles": roles, "count": len(roles)}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
