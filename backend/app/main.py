"""AI_Visage standalone local API."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.core.config import settings
from app.services.engine_service import initialize_engine

from app.api.health import router as health_router
from app.api.models import router as models_router
from app.api.faces import router as faces_router
from app.api.identities import router as identities_router
from app.api.processing import router as processing_router


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
app.include_router(faces_router, prefix=settings.api_prefix)
app.include_router(identities_router, prefix=settings.api_prefix)
app.include_router(processing_router, prefix=settings.api_prefix)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.3",
    )




    images = (
        schema["components"]["schemas"]
        ["Body_post_identity_api_identities_post"]
        ["properties"]["images"]
    )

    images["items"]["format"] = "binary"
    images["items"].pop("contentMediaType", None)

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi

@app.get("/")
def root():

    return {
        "application": settings.app_name,
        "version": settings.version,
        "status": "running",
        "docs": "/docs",
    }
