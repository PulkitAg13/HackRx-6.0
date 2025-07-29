# backend/api/__init__.py

from fastapi import APIRouter
from .upload import router as upload_router
from .query import router as query_router
from .health import router as health_router

router = APIRouter()

# Include all API route modules
router.include_router(health_router, prefix="/health", tags=["Health Check"])
router.include_router(upload_router, prefix="/upload", tags=["Document Upload"])
router.include_router(query_router, prefix="/query", tags=["Query Engine"])
