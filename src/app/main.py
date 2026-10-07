from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import engine, init_db_and_seed

from app.elastic import (
    es_client,
    init_elasticsearch,
    wait_for_elasticsearch
)
from .routers import posts, health

@asynccontextmanager
async def lifespan(app: FastAPI):
    await wait_for_elasticsearch()

    seeded_posts = await init_db_and_seed()
    await init_elasticsearch(seeded_posts)

    yield

    await es_client.close()
    await engine.dispose()

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Posts", "description": "find and delete post"}
    ]
)

app.include_router(posts)
app.include_router(health)