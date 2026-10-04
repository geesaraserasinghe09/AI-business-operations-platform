import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.init_db import init_db
from app.db.seed_data import seed_database

# API Routers
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.workflows import router as workflows_router
from app.api.tasks import router as tasks_router
from app.api.approvals import router as approvals_router
from app.api.agents import router as agents_router
from app.api.documents import router as documents_router
from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.audit import router as audit_router
from app.api.notifications import router as notifications_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: initialize database and seed demo data on startup."""
    logger.info("Starting AI Business Operations Platform API...")
    try:
        init_db()
        seed_database()
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
    yield
    logger.info("Shutting down AI Business Operations Platform API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Agentic AI-powered business operations and task automation platform orchestrated by LangGraph and Gemini.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact the platform administrator."}
    )


# Register API v1 Routers
api_v1 = settings.API_V1_STR
app.include_router(auth_router, prefix=api_v1)
app.include_router(users_router, prefix=api_v1)
app.include_router(workflows_router, prefix=api_v1)
app.include_router(tasks_router, prefix=api_v1)
app.include_router(approvals_router, prefix=api_v1)
app.include_router(agents_router, prefix=api_v1)
app.include_router(documents_router, prefix=api_v1)
app.include_router(reports_router, prefix=api_v1)
app.include_router(analytics_router, prefix=api_v1)
app.include_router(audit_router, prefix=api_v1)
app.include_router(notifications_router, prefix=api_v1)


@app.get("/health", tags=["Health"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "llm_provider": settings.LLM_PROVIDER
    }


STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

if STATIC_DIR.is_dir():
    assets_dir = STATIC_DIR / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend-assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the React dashboard from the same origin in production."""
        if full_path.startswith("api"):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Not Found"})
        candidate = STATIC_DIR / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
