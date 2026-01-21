"""
HRIS Integration Service
Handles connections to various HRIS systems (SuccessFactors, Workday, etc.)
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from app.config import settings
from app.database import init_db, get_db
from app.routers import successfactors, connections, sync, mapping, sync_history, comprehensive_sync, auto_sync
from app.middleware.audit import AuditMiddleware

security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield

app = FastAPI(
    title="HRIS Integration Service",
    description="Service for integrating with HRIS systems (SuccessFactors, Workday, etc.)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Audit middleware
app.add_middleware(AuditMiddleware)

# Include routers
app.include_router(connections.router, prefix="/api/v1/hris", tags=["Connections"])
app.include_router(successfactors.router, prefix="/api/v1/hris/successfactors", tags=["SuccessFactors"])
app.include_router(sync.router, prefix="/api/v1/hris/sync", tags=["Sync"])
app.include_router(comprehensive_sync.router, prefix="/api/v1/hris", tags=["Comprehensive Sync"])
app.include_router(auto_sync.router, prefix="/api/v1/hris", tags=["Auto Sync"])
app.include_router(mapping.router, prefix="/api/v1/hris", tags=["Field Mapping"])
app.include_router(sync_history.router, prefix="/api/v1/hris", tags=["Sync History"])

@app.get("/")
async def root():
    return {
        "service": "HRIS Integration Service",
        "version": "1.0.0",
        "status": "running",
        "supported_systems": ["SuccessFactors", "Workday", "BambooHR", "ADP", "Oracle HCM"]
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
