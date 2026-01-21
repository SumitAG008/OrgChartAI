"""
AI Chart Generator Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, Dict, Any
from datetime import datetime
from app.services.ai_chart_generator import AIChartGenerator
from app.database import get_db
from pydantic import BaseModel

router = APIRouter()
ai_generator = AIChartGenerator()

class AutoChartRequest(BaseModel):
    name: str
    description: Optional[str] = None
    source_data: Dict[str, Any]
    model_config_id: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class AutoChartResponse(BaseModel):
    id: str
    name: str
    generated_chart: Dict[str, Any]
    confidence_score: float
    processing_time_ms: int
    model_used: str
    created_at: str

@router.post("/generate-chart", response_model=AutoChartResponse)
async def generate_org_chart(
    request: AutoChartRequest,
    user_id: str = Query(..., description="User ID for audit trail"),
    db=Depends(get_db)
):
    """Auto-generate org chart using AI/ML"""
    start_time = datetime.now()
    
    try:
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

@router.get("/generated-charts")
async def list_generated_charts(
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db=Depends(get_db)
):
    """List all AI-generated org charts"""
    return await ai_generator.list_generated_charts(db, status=status, limit=limit)

@router.get("/generated-charts/{chart_id}")
async def get_generated_chart(chart_id: str, db=Depends(get_db)):
    """Get a specific AI-generated chart"""
    chart = await ai_generator.get_generated_chart(db, chart_id)
    if not chart:
        raise HTTPException(status_code=404, detail="Generated chart not found")
    return chart

@router.post("/generated-charts/{chart_id}/approve")
async def approve_generated_chart(
    chart_id: str,
    user_id: str = Query(..., description="User ID approving"),
    db=Depends(get_db)
):
    """Approve an AI-generated chart"""
    result = await ai_generator.approve_chart(db, chart_id, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Generated chart not found")
    return {"status": "approved", "chart_id": chart_id}
