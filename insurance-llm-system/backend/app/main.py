from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import router as api_router
from .core.config import settings
from .utils.logger import configure_logging

# Configure logging first
configure_logging()

app = FastAPI(
    title="Insurance LLM Processing System",
    description="API for processing insurance claims using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    from .services.document_service import initialize_document_service
    await initialize_document_service()