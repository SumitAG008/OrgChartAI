"""
Change Plan and Scenario Comparison API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.services.scenario_service import ScenarioService
from app.models import (
    Scenario, ScenarioCreate, ScenarioComparison, ChangeItem
)

router = APIRouter(prefix="/api/v1/change-plan", tags=["Change Plan"])

@router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios(
    status: Optional[str] = Query(None, description="Filter by status (Draft, Active, Archived)"),
    db: AsyncSession = Depends(get_db)
):
    """Get all scenarios"""
    service = ScenarioService()
    scenarios = await service.get_scenarios(db, status=status)
    return scenarios

@router.get("/scenarios/{scenario_id}", response_model=Scenario)
async def get_scenario(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific scenario"""
    service = ScenarioService()
    scenario = await service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenario

@router.post("/scenarios", response_model=Scenario)
async def create_scenario(
    scenario: ScenarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new scenario"""
    service = ScenarioService()
    try:
        new_scenario = await service.create_scenario(
            db=db,
            name=scenario.name,
            description=scenario.description,
            tree_id=scenario.tree_id,
            base_scenario_id=scenario.base_scenario_id,
            created_by=scenario.created_by
        )
        return new_scenario
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/scenarios/{scenario_id}/statistics")
async def get_scenario_statistics(
    scenario_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get statistics for a scenario"""
    service = ScenarioService()
    try:
        stats = await service.get_scenario_statistics(db, scenario_id)
        return stats
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/compare", response_model=ScenarioComparison)
async def compare_scenarios(
    source_scenario_id: UUID = Query(..., description="Source scenario ID"),
    target_scenario_id: UUID = Query(..., description="Target scenario ID"),
    db: AsyncSession = Depends(get_db)
):
    """Compare two scenarios and get change list"""
    service = ScenarioService()
    try:
        comparison = await service.compare_scenarios(
            db=db,
            source_scenario_id=source_scenario_id,
            target_scenario_id=target_scenario_id
        )
        return comparison
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare/{source_id}/{target_id}/changes", response_model=List[ChangeItem])
async def get_changes(
    source_id: UUID,
    target_id: UUID,
    change_type: Optional[str] = Query(None, description="Filter by change type (added, removed, updated, moved)"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (position, org_unit, employee)"),
    db: AsyncSession = Depends(get_db)
):
    """Get filtered list of changes between scenarios"""
    service = ScenarioService()
    try:
        comparison = await service.compare_scenarios(
            db=db,
            source_scenario_id=source_id,
            target_scenario_id=target_id
        )
        
        changes = comparison.changes
        
        # Apply filters
        if change_type:
            changes = [c for c in changes if c.change_type == change_type]
        
        if entity_type:
            changes = [c for c in changes if c.entity_type == entity_type]
        
        return changes
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/compare/{source_id}/{target_id}/export")
async def export_change_document(
    source_id: UUID,
    target_id: UUID,
    format: str = Query("json", description="Export format (json, pdf, docx)"),
    db: AsyncSession = Depends(get_db)
):
    """Export change document for comparison"""
    service = ScenarioService()
    try:
        comparison = await service.compare_scenarios(
            db=db,
            source_scenario_id=source_id,
            target_scenario_id=target_id
        )
        
        # TODO: Implement export logic for different formats
        # For now, return JSON
        return {
            "format": format,
            "comparison": comparison.model_dump(),
            "exported_at": comparison.compared_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
