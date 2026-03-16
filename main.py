import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from app.utils.logger import logger
from app.db.init_db import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    init_db()
    yield
    logger.info(f"Shutting down {settings.app_name}")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Smart Food & Nutrition Recommendation System",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import users, meals, recommendations

app.include_router(users.router,           prefix="/api/v1")
app.include_router(meals.router,           prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
@app.get("/", tags=["health"])
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }


@app.get("/health", tags=["health"])
async def health():
    return {"status": "healthy"}