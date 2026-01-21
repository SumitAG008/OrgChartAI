"""
Functional Chart API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.services.functional_chart_service import FunctionalChartService
from app.models import (
    FunctionCategory, FunctionCategoryCreate, FunctionCategoryUpdate,
    Function, FunctionCreate, FunctionUpdate,
    Accountability, AccountabilityCreate, AccountabilityUpdate,
    AccountabilityAssignment, AccountabilityAssignmentCreate, AccountabilityAssignmentUpdate,
    FunctionalChartResponse
)

router = APIRouter()
service = FunctionalChartService()

# ============================================
# Function Categories
# ============================================

@router.get("/categories", response_model=List[FunctionCategory])
async def get_categories(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Get all function categories"""
    return await service.get_categories(db, include_inactive=include_inactive)

@router.get("/categories/{category_id}", response_model=FunctionCategory)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific function category"""
    category = await service.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/categories", response_model=FunctionCategory, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: FunctionCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new function category"""
    return await service.create_category(db, category)

@router.put("/categories/{category_id}", response_model=FunctionCategory)
async def update_category(
    category_id: UUID,
    category: FunctionCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a function category"""
    updated = await service.update_category(db, category_id, category)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a function category"""
    success = await service.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")

# ============================================
# Functions
# ============================================

@router.get("/functions", response_model=List[Function])
async def get_functions(
    category_id: Optional[UUID] = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Get functions, optionally filtered by category"""
    return await service.get_functions(db, category_id=category_id, include_inactive=include_inactive)

@router.get("/functions/{function_id}", response_model=Function)
async def get_function(
    function_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific function"""
    function = await service.get_function(db, function_id)
    if not function:
        raise HTTPException(status_code=404, detail="Function not found")
    return function

@router.post("/functions", response_model=Function, status_code=status.HTTP_201_CREATED)
async def create_function(
    function: FunctionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new function"""
    return await service.create_function(db, function)

@router.put("/functions/{function_id}", response_model=Function)
async def update_function(
    function_id: UUID,
    function: FunctionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a function"""
    updated = await service.update_function(db, function_id, function)
    if not updated:
        raise HTTPException(status_code=404, detail="Function not found")
    return updated

@router.delete("/functions/{function_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_function(
    function_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete a function"""
    success = await service.delete_function(db, function_id)
    if not success:
        raise HTTPException(status_code=404, detail="Function not found")

# ============================================
# Accountabilities
# ============================================

@router.get("/accountabilities", response_model=List[Accountability])
async def get_accountabilities(
    function_id: Optional[UUID] = Query(default=None),
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Get accountabilities, optionally filtered by function"""
    return await service.get_accountabilities(db, function_id=function_id, include_inactive=include_inactive)

@router.get("/accountabilities/{accountability_id}", response_model=Accountability)
async def get_accountability(
    accountability_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific accountability"""
    accountability = await service.get_accountability(db, accountability_id)
    if not accountability:
        raise HTTPException(status_code=404, detail="Accountability not found")
    return accountability

@router.post("/accountabilities", response_model=Accountability, status_code=status.HTTP_201_CREATED)
async def create_accountability(
    accountability: AccountabilityCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new accountability"""
    return await service.create_accountability(db, accountability)

@router.put("/accountabilities/{accountability_id}", response_model=Accountability)
async def update_accountability(
    accountability_id: UUID,
    accountability: AccountabilityUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an accountability"""
    updated = await service.update_accountability(db, accountability_id, accountability)
    if not updated:
        raise HTTPException(status_code=404, detail="Accountability not found")
    return updated

@router.delete("/accountabilities/{accountability_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_accountability(
    accountability_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an accountability"""
    success = await service.delete_accountability(db, accountability_id)
    if not success:
        raise HTTPException(status_code=404, detail="Accountability not found")

# ============================================
# Accountability Assignments
# ============================================

@router.get("/assignments", response_model=List[AccountabilityAssignment])
async def get_assignments(
    accountability_id: Optional[UUID] = Query(default=None),
    position_id: Optional[UUID] = Query(default=None),
    employee_id: Optional[UUID] = Query(default=None),
    status: Optional[str] = Query(default=None),
    db: AsyncSession = Depends(get_db)
):
    """Get accountability assignments"""
    return await service.get_assignments(
        db,
        accountability_id=accountability_id,
        position_id=position_id,
        employee_id=employee_id,
        status=status
    )

@router.post("/assignments", response_model=AccountabilityAssignment, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment: AccountabilityAssignmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new accountability assignment"""
    return await service.create_assignment(db, assignment)

@router.put("/assignments/{assignment_id}", response_model=AccountabilityAssignment)
async def update_assignment(
    assignment_id: UUID,
    assignment: AccountabilityAssignmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an accountability assignment"""
    updated = await service.update_assignment(db, assignment_id, assignment)
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return updated

@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an accountability assignment"""
    success = await service.delete_assignment(db, assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")

# ============================================
# Full Functional Chart
# ============================================

@router.get("/chart", response_model=FunctionalChartResponse)
async def get_functional_chart(
    include_inactive: bool = Query(default=False),
    db: AsyncSession = Depends(get_db)
):
    """Get complete functional chart with all categories, functions, and accountabilities"""
    categories = await service.get_full_chart(db, include_inactive=include_inactive)
    return FunctionalChartResponse(categories=categories)
