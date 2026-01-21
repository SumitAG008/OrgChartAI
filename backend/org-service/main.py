"""
Org Service - Core Organizational Chart Service
FastAPI microservice for managing org structures, positions, and employees
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import Optional, List, Dict, Any
from datetime import date, datetime

# AI dependencies are always available
AI_AVAILABLE = True

from app.database import get_db, init_db
from app.models import (
    OrgUnit, Position, Employee,
    OrgUnitCreate, PositionCreate, EmployeeCreate,
    OrgChartResponse, TreeNode
)
from app.services.org_service import OrgService
from app.services.chart_builder import ChartBuilder
from app.services.audit_service import AuditService
from app.services.version_service import VersionService
from app.middleware.audit import AuditMiddleware
from app.config import settings
from app.routers import functional_chart, change_plan

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
    title="Org Chart Service",
    description="Core organizational chart management service",
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

# Audit middleware (tracks all changes)
app.add_middleware(AuditMiddleware)

# Initialize services
org_service = OrgService()
chart_builder = ChartBuilder()
audit_service = AuditService()
version_service = VersionService()

@app.get("/")
async def root():
    return {
        "service": "Org Chart Service",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# ============================================
# ORG UNITS
# ============================================

@app.get("/api/v1/org-units", response_model=List[OrgUnit])
async def get_org_units(
    tree_id: Optional[str] = None,
    status: Optional[str] = None,
    db=Depends(get_db)
):
    """Get all org units, optionally filtered by tree_id and status"""
    return await org_service.get_org_units(db, tree_id=tree_id, status=status)

@app.get("/api/v1/org-units/{org_unit_id}", response_model=OrgUnit)
async def get_org_unit(org_unit_id: str, db=Depends(get_db)):
    """Get a specific org unit by ID"""
    org_unit = await org_service.get_org_unit(db, org_unit_id)
    if not org_unit:
        raise HTTPException(status_code=404, detail="Org unit not found")
    return org_unit

@app.post("/api/v1/org-units", response_model=OrgUnit)
async def create_org_unit(
    org_unit: OrgUnitCreate,
    user_id: str = Query(..., description="User ID for audit trail"),
    db=Depends(get_db)
):
    """Create a new org unit"""
    from uuid import UUID
    return await org_service.create_org_unit(db, org_unit, user_id=UUID(user_id))

# ============================================
# POSITIONS
# ============================================

@app.get("/api/v1/positions", response_model=List[Position])
async def get_positions(
    org_unit_id: Optional[str] = None,
    status: Optional[str] = None,
    db=Depends(get_db)
):
    """Get all positions, optionally filtered"""
    return await org_service.get_positions(db, org_unit_id=org_unit_id, status=status)

@app.get("/api/v1/positions/{position_id}", response_model=Position)
async def get_position(position_id: str, db=Depends(get_db)):
    """Get a specific position by ID"""
    position = await org_service.get_position(db, position_id)
    if not position:
        raise HTTPException(status_code=404, detail="Position not found")
    return position

@app.post("/api/v1/positions", response_model=Position)
async def create_position(position: PositionCreate, db=Depends(get_db)):
    """Create a new position"""
    return await org_service.create_position(db, position)

@app.put("/api/v1/positions/{position_id}", response_model=Position)
async def update_position(
    position_id: str,
    position: PositionCreate,
    db=Depends(get_db)
):
    """Update a position"""
    updated = await org_service.update_position(db, position_id, position)
    if not updated:
        raise HTTPException(status_code=404, detail="Position not found")
    return updated

# ============================================
# EMPLOYEES
# ============================================

@app.get("/api/v1/employees", response_model=List[Employee])
async def get_employees(
    status: Optional[str] = None,
    org_unit_id: Optional[str] = None,
    db=Depends(get_db)
):
    """Get all employees, optionally filtered"""
    return await org_service.get_employees(db, status=status, org_unit_id=org_unit_id)

@app.get("/api/v1/employees/{employee_id}", response_model=Employee)
async def get_employee(employee_id: str, db=Depends(get_db)):
    """Get a specific employee by ID"""
    employee = await org_service.get_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

@app.post("/api/v1/employees", response_model=Employee)
async def create_employee(employee: EmployeeCreate, db=Depends(get_db)):
    """Create a new employee"""
    return await org_service.create_employee(db, employee)

@app.post("/api/v1/org-units/bulk")
async def bulk_create_org_units(
    records: Dict[str, Any],
    db=Depends(get_db)
):
    """Bulk create org units from HRIS sync"""
    from app.models_db import OrgUnit
    from uuid import UUID
    
    created = []
    errors = []
    
    for record in records.get("records", []):
        try:
            # Check if org unit already exists by hris_id
            if record.get("hris_id"):
                existing = await db.execute(
                    select(OrgUnit).where(OrgUnit.hris_id == record["hris_id"])
                )
                existing_unit = existing.scalar_one_or_none()
                if existing_unit:
                    # Update existing
                    for key, value in record.items():
                        if key != "id" and hasattr(existing_unit, key):
                            setattr(existing_unit, key, value)
                    await db.commit()
                    await db.refresh(existing_unit)
                    created.append(existing_unit.id)
                    continue
            
            # Create new
            org_unit_dict = record.copy()
            org_unit_dict.setdefault('created_by', UUID('00000000-0000-0000-0000-000000000000'))
            org_unit_dict.setdefault('status', 'Active')
            db_org_unit = OrgUnit(**org_unit_dict)
            db.add(db_org_unit)
            await db.commit()
            await db.refresh(db_org_unit)
            created.append(db_org_unit.id)
        except Exception as e:
            errors.append(f"Error creating org unit {record.get('hris_id', 'unknown')}: {str(e)}")
    
    return {"created": len(created), "errors": errors, "ids": created}

@app.post("/api/v1/positions/bulk")
async def bulk_create_positions(
    records: Dict[str, Any],
    db=Depends(get_db)
):
    """Bulk create positions from HRIS sync"""
    from app.models_db import Position
    
    created = []
    errors = []
    
    for record in records.get("records", []):
        try:
            # Check if position already exists by hris_id
            if record.get("hris_id"):
                existing = await db.execute(
                    select(Position).where(Position.hris_id == record["hris_id"])
                )
                existing_pos = existing.scalar_one_or_none()
                if existing_pos:
                    # Update existing
                    for key, value in record.items():
                        if key != "id" and hasattr(existing_pos, key):
                            setattr(existing_pos, key, value)
                    await db.commit()
                    await db.refresh(existing_pos)
                    created.append(existing_pos.id)
                    continue
            
            # Create new
            record.setdefault('status', 'Active')
            db_position = Position(**record)
            db.add(db_position)
            await db.commit()
            await db.refresh(db_position)
            created.append(db_position.id)
        except Exception as e:
            errors.append(f"Error creating position {record.get('hris_id', 'unknown')}: {str(e)}")
    
    return {"created": len(created), "errors": errors, "ids": created}

@app.post("/api/v1/employees/bulk")
async def bulk_create_employees(
    records: Dict[str, Any],
    db=Depends(get_db)
):
    """Bulk create employees from HRIS sync"""
    from app.models_db import Employee
    
    created = []
    errors = []
    
    for record in records.get("records", []):
        try:
            # Check if employee already exists by hris_id
            if record.get("hris_id"):
                existing = await db.execute(
                    select(Employee).where(Employee.hris_id == record["hris_id"])
                )
                existing_emp = existing.scalar_one_or_none()
                if existing_emp:
                    # Update existing
                    for key, value in record.items():
                        if key != "id" and hasattr(existing_emp, key):
                            setattr(existing_emp, key, value)
                    await db.commit()
                    await db.refresh(existing_emp)
                    created.append(existing_emp.id)
                    continue
            
            # Create new
            record.setdefault('status', 'Active')
            db_employee = Employee(**record)
            db.add(db_employee)
            await db.commit()
            await db.refresh(db_employee)
            created.append(db_employee.id)
        except Exception as e:
            errors.append(f"Error creating employee {record.get('hris_id', 'unknown')}: {str(e)}")
    
    return {"created": len(created), "errors": errors, "ids": created}

# ============================================
# ORG CHART
# ============================================

@app.get("/api/v1/org-chart", response_model=OrgChartResponse)
async def get_org_chart(
    org_unit_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    as_of_date: Optional[date] = None,
    max_depth: int = Query(default=10, ge=1, le=20),
    db=Depends(get_db)
):
    """
    Get organizational chart as hierarchical tree structure
    Compatible with react-org-chart and @unicef/react-org-chart
    """
    tree = await chart_builder.build_org_chart(
        db,
        org_unit_id=org_unit_id,
        scenario_id=scenario_id,
        as_of_date=as_of_date,
        max_depth=max_depth
    )
    return OrgChartResponse(tree=tree)

@app.get("/api/v1/org-chart/flat", response_model=List[TreeNode])
async def get_org_chart_flat(
    org_unit_id: Optional[str] = None,
    scenario_id: Optional[str] = None,
    db=Depends(get_db)
):
    """Get org chart as flat list of nodes"""
    return await chart_builder.build_flat_chart(
        db,
        org_unit_id=org_unit_id,
        scenario_id=scenario_id
    )

# ============================================
# METRICS
# ============================================

@app.get("/api/v1/metrics/headcount")
async def get_headcount(
    org_unit_id: Optional[str] = None,
    as_of_date: Optional[date] = None,
    db=Depends(get_db)
):
    """Get headcount metrics"""
    return await org_service.get_headcount(db, org_unit_id=org_unit_id, as_of_date=as_of_date)

@app.get("/api/v1/metrics/vacancies")
async def get_vacancies(
    org_unit_id: Optional[str] = None,
    db=Depends(get_db)
):
    """Get vacancy metrics"""
    return await org_service.get_vacancies(db, org_unit_id=org_unit_id)

@app.get("/api/v1/metrics/span-of-control")
async def get_span_of_control(
    position_id: Optional[str] = None,
    org_unit_id: Optional[str] = None,
    db=Depends(get_db)
):
    """Get span of control metrics"""
    return await org_service.get_span_of_control(
        db,
        position_id=position_id,
        org_unit_id=org_unit_id
    )

# ============================================
# AUDIT & VERSIONING
# ============================================

@app.get("/api/v1/audit/history/{table_name}/{record_id}")
async def get_audit_history(
    table_name: str,
    record_id: str,
    limit: int = Query(default=100, ge=1, le=1000),
    db=Depends(get_db)
):
    """Get change history for a record"""
    from uuid import UUID
    return await audit_service.get_change_history(
        db,
        table_name=table_name,
        record_id=UUID(record_id),
        limit=limit
    )

@app.get("/api/v1/audit/version/{table_name}/{record_id}")
async def get_version_at_time(
    table_name: str,
    record_id: str,
    timestamp: datetime = Query(...),
    db=Depends(get_db)
):
    """Get version of record at specific timestamp"""
    from uuid import UUID
    return await audit_service.get_version_at_timestamp(
        db,
        table_name=table_name,
        record_id=UUID(record_id),
        timestamp=timestamp
    )

@app.get("/api/v1/audit/changes-today")
async def get_changes_today(
    user_id: Optional[str] = None,
    db=Depends(get_db)
):
    """Get all changes made today"""
    from uuid import UUID
    return await audit_service.get_all_changes_today(
        db,
        user_id=UUID(user_id) if user_id else None
    )

# ============================================
# VERSION HISTORY
# ============================================

@app.get("/api/v1/versions/{table_name}/{record_id}")
async def get_all_versions(
    table_name: str,
    record_id: str,
    db=Depends(get_db)
):
    """Get all versions of a record"""
    from uuid import UUID
    return await version_service.get_all_versions(
        db,
        table_name=table_name,
        record_id=UUID(record_id)
    )

@app.get("/api/v1/versions/{table_name}/{record_id}/{version}")
async def get_version(
    table_name: str,
    record_id: str,
    version: int,
    db=Depends(get_db)
):
    """Get specific version of a record"""
    from uuid import UUID
    result = await version_service.get_version(
        db,
        table_name=table_name,
        record_id=UUID(record_id),
        version=version
    )
    if not result:
        raise HTTPException(status_code=404, detail="Version not found")
    return result

@app.post("/api/v1/versions/{table_name}/{record_id}/{version}/restore")
async def restore_version(
    table_name: str,
    record_id: str,
    version: int,
    user_id: str = Query(..., description="User ID restoring"),
    db=Depends(get_db)
):
    """Restore a record to a specific version"""
    from uuid import UUID
    success = await version_service.restore_version(
        db,
        table_name=table_name,
        record_id=UUID(record_id),
        version=version,
        user_id=UUID(user_id)
    )
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"status": "restored", "version": version}

# Include functional chart router
app.include_router(
    functional_chart.router,
    prefix="/api/v1/functional-chart",
    tags=["Functional Chart"]
)

# Include change plan router
app.include_router(change_plan.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
