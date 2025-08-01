from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import router as api_router
from .core.config import settings
from .utils.logger import configure_logging
import logging
from .db.session import init_db

# Configure logging first
configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events"""
    # Startup logic
    logger.info("Initializing database...")
    init_db()  # Initialize database tables
    
    # Initialize document service
    try:
        from .services.document_service import initialize_document_service
        await initialize_document_service()
        logger.info("Document service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize document service: {str(e)}")
        raise
    
    yield  # The app runs here
    
    # Shutdown logic
    logger.info("Application shutting down...")
    # Add any cleanup logic here
    # Example: await close_database_connections()

app = FastAPI(
    title="Insurance LLM Processing System",
    description="API for processing insurance claims using LLMs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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

# Optional: Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": app.version}
