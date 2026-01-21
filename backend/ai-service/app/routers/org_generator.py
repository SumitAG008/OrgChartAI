"""
AI Org Structure Generator API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.services.org_structure_generator import OrgStructureGenerator

router = APIRouter()
generator = OrgStructureGenerator()

class GenerateRequest(BaseModel):
    requirements: Dict[str, Any]
    current_structure: Optional[Dict] = None
    constraints: Optional[Dict] = None

class SaveDraftRequest(BaseModel):
    structure: Dict[str, Any]
    name: str
    description: Optional[str] = None

@router.post("/generate")
async def generate_org_structure(request: GenerateRequest):
    """Generate a recommended organizational structure"""
    try:
        result = await generator.generate_org_structure(
            requirements=request.requirements,
            current_structure=request.current_structure,
            constraints=request.constraints
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating structure: {str(e)}"
        )

@router.post("/save-draft")
async def save_as_draft(
    request: SaveDraftRequest,
    user_id: Optional[str] = None  # TODO: Get from auth token
):
    """Save generated structure as draft"""
    try:
        draft = await generator.save_as_draft(
            structure=request.structure,
            name=request.name,
            description=request.description,
            user_id=user_id
        )
        return {
            "success": True,
            "draft_id": draft["id"],
            "message": "Draft saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving draft: {str(e)}"
        )

@router.get("/recommendations/{structure_id}")
async def get_recommendations(structure_id: str):
    """Get recommendations for a structure"""
    # TODO: Load structure and generate recommendations
    return {"recommendations": []}
