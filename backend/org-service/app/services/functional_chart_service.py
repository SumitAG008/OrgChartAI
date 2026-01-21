"""
Functional Chart Service
Handles functions, accountabilities, and their assignments
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models_db import (
    FunctionCategory, Function, Accountability, AccountabilityAssignment
)
from app.models import (
    FunctionCategoryCreate, FunctionCategoryUpdate,
    FunctionCreate, FunctionUpdate,
    AccountabilityCreate, AccountabilityUpdate,
    AccountabilityAssignmentCreate, AccountabilityAssignmentUpdate
)

class FunctionalChartService:
    """Service for managing functional chart data"""
    
    # ============================================
    # Function Categories
    # ============================================
    
    async def get_categories(
        self,
        db: AsyncSession,
        include_inactive: bool = False
    ) -> List[FunctionCategory]:
        """Get all function categories"""
        query = select(FunctionCategory)
        if not include_inactive:
            query = query.where(FunctionCategory.is_active == True)
        query = query.order_by(FunctionCategory.display_order, FunctionCategory.name)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_category(
        self,
        db: AsyncSession,
        category_id: UUID
    ) -> Optional[FunctionCategory]:
        """Get a specific category with functions"""
        query = select(FunctionCategory).where(FunctionCategory.id == category_id)
        query = query.options(selectinload(FunctionCategory.functions))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_category(
        self,
        db: AsyncSession,
        category: FunctionCategoryCreate
    ) -> FunctionCategory:
        """Create a new function category"""
        try:
            db_category = FunctionCategory(**category.model_dump())
            db.add(db_category)
            await db.commit()
            await db.refresh(db_category)
            return db_category
        except Exception as e:
            await db.rollback()
            if 'does not exist' in str(e) or 'UndefinedTableError' in str(type(e).__name__):
                raise HTTPException(
                    status_code=503,
                    detail="Database tables not initialized. Please run: database/functional_chart_schema.sql"
                )
            raise
    
    async def update_category(
        self,
        db: AsyncSession,
        category_id: UUID,
        category: FunctionCategoryUpdate
    ) -> Optional[FunctionCategory]:
        """Update a function category"""
        query = select(FunctionCategory).where(FunctionCategory.id == category_id)
        result = await db.execute(query)
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            return None
        
        update_data = category.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        await db.commit()
        await db.refresh(db_category)
        return db_category
    
    async def delete_category(
        self,
        db: AsyncSession,
        category_id: UUID
    ) -> bool:
        """Delete a function category (cascades to functions and accountabilities)"""
        query = select(FunctionCategory).where(FunctionCategory.id == category_id)
        result = await db.execute(query)
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            return False
        
        await db.delete(db_category)
        await db.commit()
        return True
    
    # ============================================
    # Functions
    # ============================================
    
    async def get_functions(
        self,
        db: AsyncSession,
        category_id: Optional[UUID] = None,
        include_inactive: bool = False
    ) -> List[Function]:
        """Get functions, optionally filtered by category"""
        query = select(Function)
        
        if category_id:
            query = query.where(Function.category_id == category_id)
        
        if not include_inactive:
            query = query.where(Function.is_active == True)
        
        query = query.order_by(Function.display_order, Function.name)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_function(
        self,
        db: AsyncSession,
        function_id: UUID
    ) -> Optional[Function]:
        """Get a specific function with accountabilities"""
        query = select(Function).where(Function.id == function_id)
        query = query.options(selectinload(Function.accountabilities))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_function(
        self,
        db: AsyncSession,
        function: FunctionCreate
    ) -> Function:
        """Create a new function"""
        try:
            db_function = Function(**function.model_dump())
            db.add(db_function)
            await db.commit()
            await db.refresh(db_function)
            return db_function
        except Exception as e:
            await db.rollback()
            if 'does not exist' in str(e) or 'UndefinedTableError' in str(type(e).__name__):
                raise HTTPException(
                    status_code=503,
                    detail="Database tables not initialized. Please run: database/functional_chart_schema.sql"
                )
            raise
    
    async def update_function(
        self,
        db: AsyncSession,
        function_id: UUID,
        function: FunctionUpdate
    ) -> Optional[Function]:
        """Update a function"""
        query = select(Function).where(Function.id == function_id)
        result = await db.execute(query)
        db_function = result.scalar_one_or_none()
        
        if not db_function:
            return None
        
        update_data = function.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_function, field, value)
        
        await db.commit()
        await db.refresh(db_function)
        return db_function
    
    async def delete_function(
        self,
        db: AsyncSession,
        function_id: UUID
    ) -> bool:
        """Delete a function (cascades to accountabilities)"""
        query = select(Function).where(Function.id == function_id)
        result = await db.execute(query)
        db_function = result.scalar_one_or_none()
        
        if not db_function:
            return False
        
        await db.delete(db_function)
        await db.commit()
        return True
    
    # ============================================
    # Accountabilities
    # ============================================
    
    async def get_accountabilities(
        self,
        db: AsyncSession,
        function_id: Optional[UUID] = None,
        include_inactive: bool = False
    ) -> List[Accountability]:
        """Get accountabilities, optionally filtered by function"""
        query = select(Accountability)
        
        if function_id:
            query = query.where(Accountability.function_id == function_id)
        
        if not include_inactive:
            query = query.where(Accountability.is_active == True)
        
        query = query.order_by(Accountability.display_order)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_accountability(
        self,
        db: AsyncSession,
        accountability_id: UUID
    ) -> Optional[Accountability]:
        """Get a specific accountability with assignments"""
        query = select(Accountability).where(Accountability.id == accountability_id)
        query = query.options(selectinload(Accountability.assignments))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_accountability(
        self,
        db: AsyncSession,
        accountability: AccountabilityCreate
    ) -> Accountability:
        """Create a new accountability"""
        try:
            db_accountability = Accountability(**accountability.model_dump())
            db.add(db_accountability)
            await db.commit()
            await db.refresh(db_accountability)
            return db_accountability
        except Exception as e:
            await db.rollback()
            if 'does not exist' in str(e) or 'UndefinedTableError' in str(type(e).__name__):
                raise HTTPException(
                    status_code=503,
                    detail="Database tables not initialized. Please run the functional chart schema: database/functional_chart_schema.sql"
                )
            raise
    
    async def update_accountability(
        self,
        db: AsyncSession,
        accountability_id: UUID,
        accountability: AccountabilityUpdate
    ) -> Optional[Accountability]:
        """Update an accountability"""
        try:
            query = select(Accountability).where(Accountability.id == accountability_id)
            result = await db.execute(query)
            db_accountability = result.scalar_one_or_none()
            
            if not db_accountability:
                return None
            
            update_data = accountability.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_accountability, field, value)
            
            await db.commit()
            await db.refresh(db_accountability)
            return db_accountability
        except Exception as e:
            await db.rollback()
            if 'does not exist' in str(e) or 'UndefinedTableError' in str(type(e).__name__):
                raise HTTPException(
                    status_code=503,
                    detail="Database tables not initialized. Please run: database/functional_chart_schema.sql"
                )
            raise
    
    async def delete_accountability(
        self,
        db: AsyncSession,
        accountability_id: UUID
    ) -> bool:
        """Delete an accountability"""
        query = select(Accountability).where(Accountability.id == accountability_id)
        result = await db.execute(query)
        db_accountability = result.scalar_one_or_none()
        
        if not db_accountability:
            return False
        
        await db.delete(db_accountability)
        await db.commit()
        return True
    
    # ============================================
    # Accountability Assignments
    # ============================================
    
    async def get_assignments(
        self,
        db: AsyncSession,
        accountability_id: Optional[UUID] = None,
        position_id: Optional[UUID] = None,
        employee_id: Optional[UUID] = None,
        status: Optional[str] = None
    ) -> List[AccountabilityAssignment]:
        """Get accountability assignments with filters"""
        query = select(AccountabilityAssignment)
        
        if accountability_id:
            query = query.where(AccountabilityAssignment.accountability_id == accountability_id)
        if position_id:
            query = query.where(AccountabilityAssignment.position_id == position_id)
        if employee_id:
            query = query.where(AccountabilityAssignment.employee_id == employee_id)
        if status:
            query = query.where(AccountabilityAssignment.status == status)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create_assignment(
        self,
        db: AsyncSession,
        assignment: AccountabilityAssignmentCreate
    ) -> AccountabilityAssignment:
        """Create a new accountability assignment"""
        db_assignment = AccountabilityAssignment(**assignment.model_dump())
        db.add(db_assignment)
        await db.commit()
        await db.refresh(db_assignment)
        return db_assignment
    
    async def update_assignment(
        self,
        db: AsyncSession,
        assignment_id: UUID,
        assignment: AccountabilityAssignmentUpdate
    ) -> Optional[AccountabilityAssignment]:
        """Update an accountability assignment"""
        query = select(AccountabilityAssignment).where(AccountabilityAssignment.id == assignment_id)
        result = await db.execute(query)
        db_assignment = result.scalar_one_or_none()
        
        if not db_assignment:
            return None
        
        update_data = assignment.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_assignment, field, value)
        
        await db.commit()
        await db.refresh(db_assignment)
        return db_assignment
    
    async def delete_assignment(
        self,
        db: AsyncSession,
        assignment_id: UUID
    ) -> bool:
        """Delete an accountability assignment"""
        query = select(AccountabilityAssignment).where(AccountabilityAssignment.id == assignment_id)
        result = await db.execute(query)
        db_assignment = result.scalar_one_or_none()
        
        if not db_assignment:
            return False
        
        await db.delete(db_assignment)
        await db.commit()
        return True
    
    # ============================================
    # Full Functional Chart
    # ============================================
    
    async def get_full_chart(
        self,
        db: AsyncSession,
        include_inactive: bool = False
    ) -> List[FunctionCategory]:
        """Get complete functional chart with all categories, functions, and accountabilities"""
        try:
            query = select(FunctionCategory)
            if not include_inactive:
                query = query.where(FunctionCategory.is_active == True)
            query = query.order_by(FunctionCategory.display_order, FunctionCategory.name)
            
            # Eager load functions and their accountabilities
            query = query.options(
                selectinload(FunctionCategory.functions).selectinload(Function.accountabilities)
            )
            
            result = await db.execute(query)
            categories = result.scalars().all()
            
            # Count assignments for each accountability
            for category in categories:
                for function in category.functions:
                    for accountability in function.accountabilities:
                        assignment_count_query = select(func.count(AccountabilityAssignment.id)).where(
                            and_(
                                AccountabilityAssignment.accountability_id == accountability.id,
                                AccountabilityAssignment.status == 'Active'
                            )
                        )
                        assignment_count_result = await db.execute(assignment_count_query)
                        accountability.assignment_count = assignment_count_result.scalar() or 0
            
            return categories
        except Exception as e:
            # If tables don't exist, return mock data
            if 'does not exist' in str(e) or 'UndefinedTableError' in str(type(e).__name__):
                print(f"Database error (tables may not exist): {e}")
                print("Returning mock functional chart data...")
                return self._get_mock_chart_data()
            raise
    
    def _get_mock_chart_data(self) -> List[FunctionCategory]:
        """Return mock functional chart data when database tables don't exist"""
        from uuid import uuid4
        from datetime import datetime
        
        # Generate realistic mock data based on common organizational structures
        people_culture_id = uuid4()
        governance_id = uuid4()
        brand_comm_id = uuid4()
        account_mgmt_id = uuid4()
        legal_compliance_id = uuid4()
        
        # Create function IDs
        comp_id = uuid4()
        recruit_id = uuid4()
        talent_id = uuid4()
        perf_mgmt_id = uuid4()
        board_gov_id = uuid4()
        ethics_id = uuid4()
        brand_strategy_id = uuid4()
        comm_delivery_id = uuid4()
        account_growth_id = uuid4()
        qbr_mgmt_id = uuid4()
        legal_counsel_id = uuid4()
        ip_mgmt_id = uuid4()
        
        mock_categories = [
            FunctionCategory(
                id=people_culture_id,
                name="People and Culture",
                description="Human resources and organizational culture functions",
                icon="👥",
                display_order=1,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=uuid4(),
                updated_by=None,
                version=1,
                functions=[
                    Function(
                        id=comp_id,
                        category_id=people_culture_id,
                        name="Compensation",
                        icon="💰",
                        display_order=1,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[
                            Accountability(
                                id=uuid4(),
                                function_id=comp_id,
                                objective="Operate remuneration, incentives and benefit programs to attract, compensate and retain quality employees",
                                display_order=0,
                                is_active=True,
                                created_at=datetime.now(),
                                updated_at=datetime.now(),
                                created_by=uuid4(),
                                updated_by=None,
                                version=1
                            )
                        ]
                    ),
                    Function(
                        id=recruit_id,
                        category_id=people_culture_id,
                        name="Recruitment",
                        icon="🔍",
                        display_order=2,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=talent_id,
                        category_id=people_culture_id,
                        name="Talent Development",
                        icon="⭐",
                        display_order=3,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=perf_mgmt_id,
                        category_id=people_culture_id,
                        name="Performance Management",
                        icon="📈",
                        display_order=4,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    )
                ]
            ),
            FunctionCategory(
                id=governance_id,
                name="Governance",
                description="Corporate governance and compliance",
                icon="⚖️",
                display_order=2,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=uuid4(),
                updated_by=None,
                version=1,
                functions=[
                    Function(
                        id=board_gov_id,
                        category_id=governance_id,
                        name="Board Governance",
                        icon="👔",
                        display_order=1,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=ethics_id,
                        category_id=governance_id,
                        name="Corporate Ethics and Compliance",
                        icon="⚖️",
                        display_order=2,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    )
                ]
            ),
            FunctionCategory(
                id=brand_comm_id,
                name="Brand and Communications",
                description="Brand management and communications",
                icon="📣",
                display_order=3,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=uuid4(),
                updated_by=None,
                version=1,
                functions=[
                    Function(
                        id=brand_strategy_id,
                        category_id=brand_comm_id,
                        name="Brand Strategy",
                        icon="🎨",
                        display_order=1,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=comm_delivery_id,
                        category_id=brand_comm_id,
                        name="Communications Delivery",
                        icon="📧",
                        display_order=2,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    )
                ]
            ),
            FunctionCategory(
                id=account_mgmt_id,
                name="Account Management",
                description="Client account management and relationships",
                icon="🤝",
                display_order=4,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=uuid4(),
                updated_by=None,
                version=1,
                functions=[
                    Function(
                        id=account_growth_id,
                        category_id=account_mgmt_id,
                        name="Account Growth",
                        icon="📈",
                        display_order=1,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=qbr_mgmt_id,
                        category_id=account_mgmt_id,
                        name="Quarterly Business Review Management",
                        icon="📊",
                        display_order=2,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    )
                ]
            ),
            FunctionCategory(
                id=legal_compliance_id,
                name="Commercial, Compliance and Legal",
                description="Legal, compliance, and commercial functions",
                icon="📋",
                display_order=5,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=uuid4(),
                updated_by=None,
                version=1,
                functions=[
                    Function(
                        id=legal_counsel_id,
                        category_id=legal_compliance_id,
                        name="Legal Counsel and Management",
                        icon="👨‍⚖️",
                        display_order=1,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    ),
                    Function(
                        id=ip_mgmt_id,
                        category_id=legal_compliance_id,
                        name="Intellectual Property Management",
                        icon="©️",
                        display_order=2,
                        is_active=True,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=uuid4(),
                        updated_by=None,
                        version=1,
                        accountabilities=[]
                    )
                ]
            )
        ]
        
        # Set assignment_count as a Python attribute (not a DB column) for all accountabilities
        for category in mock_categories:
            for function in category.functions:
                for accountability in function.accountabilities:
                    # assignment_count is not a DB column, so set it as a regular attribute
                    setattr(accountability, 'assignment_count', 0)
        
        return mock_categories
