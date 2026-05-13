"""FastAPI application factory"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from sqlalchemy import text

from app.config import settings
from app.api import auth, users, cases, evidence, notifications, admin
from app.api import demo
from app.db.database import AsyncSessionLocal, init_db
from app.auth.otp_handler import redis_client
from app.services.demo import seed_demo_data
import logging

# Setup logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    await init_db()
    if settings.DEMO_MODE and settings.AUTO_SEED_DEMO_DATA:
        async with AsyncSessionLocal() as session:
            try:
                result = await seed_demo_data(session)
                logger.info("Demo seed result: %s", result.get("message"))
            except Exception as exc:
                logger.error("Demo seed failed: %s", exc)
    logger.info(f"Starting Hear My Case API (v{settings.APP_VERSION}) in {settings.ENVIRONMENT} mode")
    yield
    # Shutdown
    logger.info("Shutting down Hear My Case API")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Legal case management platform for workers in India",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": settings.APP_VERSION,
            "demo_mode": settings.DEMO_MODE,
        }

    @app.get("/health/ready", tags=["Health"])
    async def readiness_check():
        """Readiness endpoint."""
        db_ready = False
        redis_ready = False

        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
                db_ready = True
        except Exception as exc:
            logger.warning("Readiness DB check failed: %s", exc)

        try:
            redis_ready = bool(redis_client.ping())
        except Exception as exc:
            logger.warning("Readiness Redis check failed: %s", exc)

        return {
            "status": "ready" if db_ready and redis_ready else "degraded",
            "database": db_ready,
            "redis": redis_ready,
            "demo_mode": settings.DEMO_MODE,
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Hear My Case API",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        }
    
    # Include routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(cases.router)
    app.include_router(evidence.router)
    app.include_router(notifications.router)
    app.include_router(admin.router)
    app.include_router(demo.router)
    
    logger.info("FastAPI application created successfully")
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
