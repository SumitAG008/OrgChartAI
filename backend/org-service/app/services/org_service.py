"""
Org Service - Business logic for org units, positions, and employees
"""

from typing import Optional, List
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from app.models import (
    OrgUnit as OrgUnitModel, OrgUnitCreate,
    Position as PositionModel, PositionCreate,
    Employee as EmployeeModel, EmployeeCreate
)
from app.models_db import OrgUnit, Position, Employee

class OrgService:
    """Service for managing organizational data"""
    
    async def get_org_units(
        self,
        db: AsyncSession,
        tree_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[OrgUnitModel]:
        """Get all org units with optional filters"""
        query = select(OrgUnit)
        
        if tree_id:
            query = query.where(OrgUnit.tree_id == tree_id)
        if status:
            query = query.where(OrgUnit.status == status)
        
        result = await db.execute(query)
        db_units = result.scalars().all()
        # Convert SQLAlchemy models to Pydantic models
        return [OrgUnitModel.model_validate(unit) for unit in db_units]
    
    async def get_org_unit(
        self,
        db: AsyncSession,
        org_unit_id: UUID
    ) -> Optional[OrgUnitModel]:
        """Get a specific org unit"""
        query = select(OrgUnit).where(OrgUnit.id == org_unit_id)
        result = await db.execute(query)
        db_unit = result.scalar_one_or_none()
        return OrgUnitModel.model_validate(db_unit) if db_unit else None
    
    async def create_org_unit(
        self,
        db: AsyncSession,
        org_unit: OrgUnitCreate,
        user_id: Optional[UUID] = None
    ) -> OrgUnitModel:
        """Create a new org unit"""
        org_unit_dict = org_unit.dict()
        org_unit_dict['created_by'] = user_id or UUID('00000000-0000-0000-0000-000000000000')
        org_unit_dict['updated_by'] = user_id
        db_org_unit = OrgUnit(**org_unit_dict)
        db.add(db_org_unit)
        await db.commit()
        await db.refresh(db_org_unit)
        return OrgUnitModel.model_validate(db_org_unit)
    
    async def get_positions(
        self,
        db: AsyncSession,
        org_unit_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[Position]:
        """Get all positions with optional filters"""
        query = select(Position)
        
        if org_unit_id:
            query = query.where(Position.org_unit_id == org_unit_id)
        if status:
            query = query.where(Position.status == status)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_position(
        self,
        db: AsyncSession,
        position_id: UUID
    ) -> Optional[Position]:
        """Get a specific position"""
        query = select(Position).where(Position.id == position_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_position(
        self,
        db: AsyncSession,
        position: PositionCreate
    ) -> Position:
        """Create a new position"""
        db_position = Position(**position.dict())
        db.add(db_position)
        await db.commit()
        await db.refresh(db_position)
        return db_position
    
    async def update_position(
        self,
        db: AsyncSession,
        position_id: UUID,
        position: PositionCreate
    ) -> Optional[Position]:
        """Update a position"""
        db_position = await self.get_position(db, position_id)
        if not db_position:
            return None
        
        for key, value in position.dict().items():
            setattr(db_position, key, value)
        
        await db.commit()
        await db.refresh(db_position)
        return db_position
    
    async def get_employees(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        org_unit_id: Optional[UUID] = None
    ) -> List[Employee]:
        """Get all employees with optional filters"""
        query = select(Employee)
        
        if status:
            query = query.where(Employee.status == status)
        if org_unit_id:
            query = query.join(Position).where(Position.org_unit_id == org_unit_id)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_employee(
        self,
        db: AsyncSession,
        employee_id: UUID
    ) -> Optional[Employee]:
        """Get a specific employee"""
        query = select(Employee).where(Employee.id == employee_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_employee(
        self,
        db: AsyncSession,
        employee: EmployeeCreate
    ) -> Employee:
        """Create a new employee"""
        db_employee = Employee(**employee.dict())
        db.add(db_employee)
        await db.commit()
        await db.refresh(db_employee)
        return db_employee
    
    async def get_headcount(
        self,
        db: AsyncSession,
        org_unit_id: Optional[UUID] = None,
        as_of_date: Optional[date] = None
    ) -> dict:
        """Calculate headcount metrics"""
        query = select(func.count(Employee.id)).where(
            Employee.status == 'Active'
        )
        
        if org_unit_id:
            query = query.join(Position).where(Position.org_unit_id == org_unit_id)
        
        result = await db.execute(query)
        count = result.scalar()
        
        return {
            "headcount": count,
            "org_unit_id": str(org_unit_id) if org_unit_id else None,
            "as_of_date": as_of_date.isoformat() if as_of_date else None
        }
    
    async def get_vacancies(
        self,
        db: AsyncSession,
        org_unit_id: Optional[UUID] = None
    ) -> dict:
        """Get vacancy metrics"""
        # Positions with no active primary assignment
        query = select(func.count(Position.id)).where(
            Position.status == 'Active'
        )
        
        if org_unit_id:
            query = query.where(Position.org_unit_id == org_unit_id)
        
        result = await db.execute(query)
        total_positions = result.scalar()
        
        # TODO: Subtract positions with active assignments
        vacant_count = total_positions  # Simplified
        
        return {
            "vacant_positions": vacant_count,
            "total_positions": total_positions,
            "vacancy_rate": vacant_count / total_positions if total_positions > 0 else 0
        }
    
    async def get_span_of_control(
        self,
        db: AsyncSession,
        position_id: Optional[UUID] = None,
        org_unit_id: Optional[UUID] = None
    ) -> dict:
        """Calculate span of control metrics"""
        # Count direct reports
        query = select(func.count(Position.id)).where(
            Position.reports_to_position_id == position_id,
            Position.status == 'Active'
        )
        
        result = await db.execute(query)
        direct_reports = result.scalar()
        
        return {
            "position_id": str(position_id) if position_id else None,
            "direct_reports": direct_reports,
            "span_of_control": direct_reports
        }
