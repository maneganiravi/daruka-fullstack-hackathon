from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import analytics, auth, projects, sites
from app.core.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables and seed data on startup
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    description="Full-Stack Geospatial Environmental Monitoring Platform with PostGIS & Mapbox GL JS.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set CORS middleware
if settings.parsed_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.parsed_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(projects.router, prefix=settings.API_V1_STR)
app.include_router(sites.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["Health"])
@app.get("/api/health", tags=["Health"])
def health():
    return {"status": "ok"}


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/health",
    }
