from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.endpoints import router as api_router
from .core.config import settings
from .utils.logger import configure_logging
from backend.app.db.session import init_db
from .services.document_service import initialize_document_service

# Configure logging before anything else
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and Shutdown logic"""
    # --- Startup ---
    init_db()  # Synchronous DB initialization
    app.logger.info("✅ Database initialized")

    await initialize_document_service()  # Async doc service
    app.logger.info("✅ Document service initialized")

    yield  # Application runs here

    # --- Shutdown (if needed) ---
    # await cleanup_resources()
    app.logger.info("🛑 Application shutdown complete")

# Instantiate FastAPI app
app = FastAPI(
    title="Insurance LLM Processing System",
    description="API for processing insurance claims using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
