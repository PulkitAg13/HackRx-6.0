from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import router as api_router
from .core.config import settings
from .utils.logger import configure_logging

# Configure logging first
configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup logic
    from .services.document_service import initialize_document_service
    await initialize_document_service()
    
    yield  # The app runs here
    
    # Shutdown logic (if any)
    # await cleanup_resources()

app = FastAPI(
    title="Insurance LLM Processing System",
    description="API for processing insurance claims using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan  # Add lifespan handler here
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")