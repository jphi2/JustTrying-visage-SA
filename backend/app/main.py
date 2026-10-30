"""AI_Visage standalone local API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.services.engine_service import initialize_engine

from app.api.health import router as health_router
from app.api.models import router as models_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    initialize_engine()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Standalone local face processing application.",
    lifespan=lifespan,
)

# Local development frontend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(
    health_router,
    prefix=settings.api_prefix,
)

app.include_router(
    models_router,
    prefix=settings.api_prefix,
)


@app.get("/")
def root():

    return {
        "application": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
    }
