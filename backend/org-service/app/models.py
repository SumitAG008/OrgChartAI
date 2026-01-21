"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID

# Person and TreeNode models for org chart
class Person(BaseModel):
    name: str
    title: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[EmailStr] = None
    employment_type: Optional[str] = None
    position_type: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class TreeNode(BaseModel):
    id: str
    person: Person
    hasChild: bool
    hasParent: bool
    isHighlight: bool = False
    children: Optional[List['TreeNode']] = None

    model_config = ConfigDict(from_attributes=True)

TreeNode.model_rebuild()

class OrgChartResponse(BaseModel):
    tree: TreeNode
    metadata: Optional[Dict[str, Any]] = None

# ============================================
# Org Unit Models
# ============================================

class OrgUnitBase(BaseModel):
    code: str
    name: str
    parent_org_unit_id: Optional[UUID] = None
    type: str
    cost_center_id: Optional[UUID] = None
    location_id: Optional[UUID] = None
    legal_entity_id: Optional[UUID] = None
    scope: Optional[str] = None
    tree_id: Optional[str] = None
    effective_start_date: date
    effective_end_date: Optional[date] = None
    status: str = "Active"

class OrgUnitCreate(OrgUnitBase):
    created_by: UUID

class OrgUnit(OrgUnitBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

# ============================================
# Position Models
# ============================================

class PositionBase(BaseModel):
    org_unit_id: UUID
    job_id: Optional[UUID] = None
    position_code: str
    position_title: str
    position_type: str
    reports_to_position_id: Optional[UUID] = None
    fte: float = 1.0
    grade: Optional[str] = None
    level: Optional[int] = None
    is_managerial: bool = False
    is_mass_position_template: bool = False
    status: str = "Active"
    effective_start_date: date
    effective_end_date: Optional[date] = None

class PositionCreate(PositionBase):
    created_by: UUID

class Position(PositionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

# ============================================
# Employee Models
# ============================================

class EmployeeBase(BaseModel):
    employee_number: str
    first_name: str
    last_name: str
    preferred_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hire_date: Optional[date] = None
    termination_date: Optional[date] = None
    status: str = "Active"
    position_id: Optional[UUID] = None
    hris_id: Optional[str] = None
    hris_source: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    created_by: UUID

class Employee(EmployeeBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

# ============================================
# Scenario Models (Change Plan)
# ============================================

class ScenarioBase(BaseModel):
    name: str
    description: Optional[str] = None
    tree_id: str
    base_scenario_id: Optional[UUID] = None
    status: str = "Draft"  # Draft, Active, Archived

class ScenarioCreate(ScenarioBase):
    created_by: UUID

class Scenario(ScenarioBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)

# ============================================
# Change Comparison Models
# ============================================

class ChangeItem(BaseModel):
    """Represents a single change between scenarios"""
    change_type: str  # "added", "removed", "updated", "moved"
    entity_type: str  # "position", "org_unit", "employee"
    entity_id: UUID
    entity_name: str
    old_value: Optional[Dict[str, Any]] = None
    new_value: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Dict[str, Any]]] = None  # field_name: {old: x, new: y}

class ScenarioComparison(BaseModel):
    """Comparison between two scenarios"""
    source_scenario_id: UUID
    source_scenario_name: str
    target_scenario_id: UUID
    target_scenario_name: str
    changes: List[ChangeItem]
    summary: Dict[str, int]  # {"added": 5, "removed": 3, "updated": 10, "moved": 2}
    compared_at: datetime

# ============================================
# Functional Chart Models
# ============================================

class FunctionCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class FunctionCategoryCreate(FunctionCategoryBase):
    pass

class FunctionCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class FunctionCategory(FunctionCategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

class FunctionBase(BaseModel):
    category_id: UUID
    name: str
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class FunctionCreate(FunctionBase):
    pass

class FunctionUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class Function(FunctionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

class AccountabilityBase(BaseModel):
    function_id: UUID
    name: str
    description: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class AccountabilityCreate(AccountabilityBase):
    pass

class AccountabilityUpdate(BaseModel):
    function_id: Optional[UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class Accountability(AccountabilityBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    version: int
    assignment_count: int = 0  # Computed field

    model_config = ConfigDict(from_attributes=True)

class AccountabilityAssignmentBase(BaseModel):
    accountability_id: UUID
    position_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None
    assignment_type: str = "Primary"  # Primary, Secondary, Shared
    is_active: bool = True

class AccountabilityAssignmentCreate(AccountabilityAssignmentBase):
    pass

class AccountabilityAssignmentUpdate(BaseModel):
    accountability_id: Optional[UUID] = None
    position_id: Optional[UUID] = None
    org_unit_id: Optional[UUID] = None
    assignment_type: Optional[str] = None
    is_active: Optional[bool] = None

class AccountabilityAssignment(AccountabilityAssignmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[UUID] = None
    updated_by: Optional[UUID] = None
    version: int

    model_config = ConfigDict(from_attributes=True)

# ============================================
# Functional Chart Response Models
# ============================================

class FunctionalChartResponse(BaseModel):
    categories: List[FunctionCategory]
    
    model_config = ConfigDict(from_attributes=True)
