"""
AI Service - AI/ML Powered Org Chart Generation
Uses MCP (Model Context Protocol) and AI models for auto org chart visualization
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from app.config import settings
from app.services.ai_chart_generator import AIChartGenerator
from app.services.mcp_client import MCPClient
from app.database import get_db, init_db
from app.routers import chart_generator, org_generator

# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass

# Create FastAPI app
app = FastAPI(
    title="AI Org Chart Service",
    description="AI-powered org chart generation and recommendations",
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

# Initialize services
ai_generator = AIChartGenerator()
mcp_client = MCPClient()

# Include routers
app.include_router(chart_generator.router, prefix="/api/v1/ai", tags=["AI Chart Generator"])
app.include_router(org_generator.router, prefix="/api/v1/ai/org", tags=["Org Structure Generator"])

@app.get("/")
async def root():
    return {
        "service": "AI Org Chart Service",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ============================================
# AI ORG CHART GENERATION
# ============================================

class AutoChartRequest(BaseModel):
    """Request for auto-generating org chart"""
    name: str
    description: Optional[str] = None
    source_data: Dict[str, Any]  # HRIS data, CSV, or manual input
    model_config_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None  # Layout preferences, etc.

class AutoChartResponse(BaseModel):
    """Response with generated org chart"""
    id: str
    name: str
    generated_chart: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int
    model_used: str
    created_at: str

@app.post("/api/v1/ai/generate-chart", response_model=AutoChartResponse)
async def generate_org_chart(
    request: AutoChartRequest,
    user_id: str = Query(..., description="User ID for audit trail"),
    db=Depends(get_db)
):
    """
    Auto-generate org chart using AI/ML
    Uses MCP and AI models to create org structure from source data
    """
    start_time = datetime.now()
    
    try:
        # Generate org chart using AI
        result = await ai_generator.generate_chart(
            source_data=request.source_data,
            preferences=request.preferences,
            model_config_id=request.model_config_id,
            user_id=user_id
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AutoChartResponse(
            id=result["id"],
            name=request.name,
            generated_chart=result["chart"],
            confidence_score=result["confidence_score"],
            processing_time_ms=processing_time,
            model_used=result["model_name"],
            created_at=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

@app.get("/api/v1/ai/generated-charts")
async def list_generated_charts(
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db=Depends(get_db)
):
    """List all AI-generated org charts"""
    return await ai_generator.list_generated_charts(db, status=status, limit=limit)

@app.get("/api/v1/ai/generated-charts/{chart_id}")
async def get_generated_chart(chart_id: str, db=Depends(get_db)):
    """Get a specific AI-generated chart"""
    chart = await ai_generator.get_generated_chart(db, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Generated chart not found")
    return chart

@app.post("/api/v1/ai/generated-charts/{chart_id}/approve")
async def approve_generated_chart(
    chart_id: str,
    user_id: str = Query(..., description="User ID approving"),
    db=Depends(get_db)
):
    """Approve an AI-generated chart (moves to production)"""
    result = await ai_generator.approve_chart(db, chart_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Generated chart not found")
    return {"status": "approved", "chart_id": chart_id}

# ============================================
# AI RECOMMENDATIONS
# ============================================

@app.post("/api/v1/ai/recommendations/team-formation")
async def recommend_team(
    project_requirements: Dict[str, Any],
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """AI recommendation for team formation"""
    return await ai_generator.recommend_team(db, project_requirements, user_id)

@app.post("/api/v1/ai/recommendations/org-design")
async def recommend_org_design(
    current_org: Dict[str, Any],
    objectives: Dict[str, Any],
    user_id: str = Query(..., description="User ID"),
    db=Depends(get_db)
):
    """AI recommendation for org design improvements"""
    return await ai_generator.recommend_org_design(db, current_org, objectives, user_id)

# ============================================
# MCP INTEGRATION
# ============================================

@app.get("/api/v1/ai/mcp/models")
async def list_mcp_models():
    """List available MCP models"""
    return await mcp_client.list_available_models()

@app.post("/api/v1/ai/mcp/generate")
async def mcp_generate(
    prompt: str,
    model: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
):
    """Generate using MCP"""
    return await mcp_client.generate(prompt, model=model, context=context)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )
