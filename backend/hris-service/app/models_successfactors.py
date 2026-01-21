"""
SuccessFactors Data Models - Aligned with actual SF OData API structure
These models match the exact field names and structure returned by SuccessFactors
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

# ============================================
# Foundation Object (FO) Models
# ============================================

class FOBusinessUnit(BaseModel):
    """FOBusinessUnit - Foundation Object for Business Units"""
    # Primary Fields
    externalCode: str  # Primary key
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None  # "A" = Active, "I" = Inactive
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Hierarchy
    parent: Optional[str] = None  # externalCode of parent
    head: Optional[str] = None  # userId of head

    # Additional Fields
    description: Optional[str] = None
    description_defaultValue: Optional[str] = None
    cust_country: Optional[str] = None
    cust_region: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"  # Allow additional fields from SuccessFactors

class FODepartment(BaseModel):
    """FODepartment - Foundation Object for Departments"""
    externalCode: str
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Hierarchy
    parent: Optional[str] = None
    head: Optional[str] = None
    division: Optional[str] = None
    businessUnit: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

class FODivision(BaseModel):
    """FODivision - Foundation Object for Divisions"""
    externalCode: str
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Hierarchy
    parent: Optional[str] = None
    head: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

class FOCostCenter(BaseModel):
    """FOCostCenter - Foundation Object for Cost Centers"""
    externalCode: str
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Hierarchy
    parent: Optional[str] = None
    costCenterManager: Optional[str] = None

    # Additional
    description: Optional[str] = None
    description_defaultValue: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

class FOLegalEntity(BaseModel):
    """FOLegalEntity - Foundation Object for Legal Entities"""
    externalCode: str
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Location
    country: Optional[str] = None
    defaultLocation: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

class FOLocation(BaseModel):
    """FOLocation - Foundation Object for Locations"""
    externalCode: str
    name_defaultValue: Optional[str] = None
    name_en_US: Optional[str] = None
    status: Optional[str] = None
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Address
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

# ============================================
# Employee Data Models
# ============================================

class User(BaseModel):
    """User - Main employee entity in SuccessFactors"""
    userId: str  # Primary key
    username: Optional[str] = None
    email: Optional[str] = None

    # Name fields
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    displayName: Optional[str] = None
    preferredName: Optional[str] = None

    # Employment
    status: Optional[str] = None  # "t" = active, "f" = inactive
    empId: Optional[str] = None  # Employee ID
    personIdExternal: Optional[str] = None

    # Organization
    department: Optional[str] = None
    division: Optional[str] = None
    location: Optional[str] = None
    businessUnit: Optional[str] = None

    # Manager
    manager: Optional[str] = None  # userId of manager
    hr: Optional[str] = None  # userId of HR rep

    # Dates
    hireDate: Optional[date] = None
    lastModifiedDateTime: Optional[datetime] = None

    # Custom fields (common ones)
    custom01: Optional[str] = None  # Often employee number
    custom02: Optional[str] = None
    custom03: Optional[str] = None

    class Config:
        extra = "allow"

class PerPerson(BaseModel):
    """PerPerson - Personal Information entity"""
    personIdExternal: str  # Primary key
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    preferredName: Optional[str] = None

    # Dates
    dateOfBirth: Optional[date] = None

    # Contact
    personalInfoNav: Optional[Dict] = None

    class Config:
        extra = "allow"

class EmpEmployment(BaseModel):
    """EmpEmployment - Employment Information"""
    personIdExternal: str
    userId: str

    # Dates
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Status
    assignmentClass: Optional[str] = None  # "E" = Employee, "C" = Contingent
    isECRecord: Optional[bool] = None
    isPrimary: Optional[bool] = None

    class Config:
        extra = "allow"

class EmpJob(BaseModel):
    """EmpJob - Job Assignment Information"""
    userId: str
    seqNumber: Optional[str] = None

    # Dates
    startDate: Optional[date] = None
    endDate: Optional[date] = None

    # Job
    position: Optional[str] = None  # Position code
    jobCode: Optional[str] = None
    jobTitle: Optional[str] = None

    # Organization
    department: Optional[str] = None
    division: Optional[str] = None
    location: Optional[str] = None
    businessUnit: Optional[str] = None
    company: Optional[str] = None
    costCenter: Optional[str] = None

    # Manager
    managerId: Optional[str] = None
    managerPosition: Optional[str] = None

    # Employment
    emplStatus: Optional[str] = None
    employmentType: Optional[str] = None

    # FTE
    standardHours: Optional[float] = None
    timeTypeNav: Optional[Dict] = None

    class Config:
        extra = "allow"

# ============================================
# Position Models
# ============================================

class Position(BaseModel):
    """Position - Position entity"""
    code: str  # Primary key (position code)
    externalName_defaultValue: Optional[str] = None
    externalName_en_US: Optional[str] = None

    # Dates
    effectiveStartDate: Optional[date] = None
    effectiveEndDate: Optional[date] = None

    # Job
    jobCode: Optional[str] = None
    jobLevel: Optional[str] = None

    # Organization
    department: Optional[str] = None
    division: Optional[str] = None
    businessUnit: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    costCenter: Optional[str] = None

    # Reporting
    parentPosition: Optional[str] = None

    # Status
    type: Optional[str] = None
    standardHours: Optional[float] = None

    # Incumbent
    incumbent: Optional[str] = None  # userId

    # Metadata
    createdBy: Optional[str] = None
    createdDateTime: Optional[datetime] = None
    lastModifiedBy: Optional[str] = None
    lastModifiedDateTime: Optional[datetime] = None

    class Config:
        extra = "allow"

# ============================================
# Response Wrappers
# ============================================

class ODataResponse(BaseModel):
    """Standard OData response wrapper"""
    d: Dict[str, Any]

    class Config:
        extra = "allow"

class ODataResultsResponse(BaseModel):
    """OData response with results array"""
    results: List[Dict[str, Any]]
    __count: Optional[int] = None
    __next: Optional[str] = None

    class Config:
        extra = "allow"

# ============================================
# Mapping Configuration
# ============================================

# Default field mappings from SuccessFactors to OrgChartAI
SF_TO_ORGCHART_MAPPINGS = {
    "FOBusinessUnit": {
        "entity_type": "org_unit",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",  # Fallback
            "status": "status",  # Transform: "A" -> "Active", "I" -> "Inactive"
            "parent": "parent_org_unit_id",  # Lookup
            "head": "manager_user_id",  # Lookup
            "startDate": "effective_start_date",
            "endDate": "effective_end_date",
            "description_defaultValue": "description",
        },
        "type": "Business Unit"
    },
    "FODepartment": {
        "entity_type": "org_unit",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",
            "status": "status",
            "parent": "parent_org_unit_id",
            "businessUnit": "parent_org_unit_id",  # Alternative parent
            "division": "parent_org_unit_id",  # Alternative parent
            "head": "manager_user_id",
            "startDate": "effective_start_date",
            "endDate": "effective_end_date",
        },
        "type": "Department"
    },
    "FODivision": {
        "entity_type": "org_unit",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",
            "status": "status",
            "parent": "parent_org_unit_id",
            "head": "manager_user_id",
            "startDate": "effective_start_date",
            "endDate": "effective_end_date",
        },
        "type": "Division"
    },
    "FOCostCenter": {
        "entity_type": "cost_center",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",
            "status": "status",
            "parent": "parent_cost_center_id",
            "startDate": "effective_start_date",
            "endDate": "effective_end_date",
        }
    },
    "FOLegalEntity": {
        "entity_type": "legal_entity",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",
            "country": "country",
            "status": "status",
            "startDate": "effective_start_date",
            "endDate": "effective_end_date",
        }
    },
    "FOLocation": {
        "entity_type": "location",
        "fields": {
            "externalCode": "code",
            "name_defaultValue": "name",
            "name_en_US": "name",
            "city": "city",
            "country": "country",
            "zipCode": "zip_code",
        }
    },
    "User": {
        "entity_type": "employee",
        "fields": {
            "userId": "employee_number",
            "empId": "employee_number",  # Fallback
            "custom01": "employee_number",  # Often used for employee ID
            "firstName": "first_name",
            "lastName": "last_name",
            "middleName": "middle_name",
            "preferredName": "preferred_name",
            "email": "email",
            "status": "status",  # Transform: "t" -> "Active", "f" -> "Terminated"
            "department": "org_unit_code",  # Lookup
            "manager": "manager_user_id",
            "hireDate": "hire_date",
        }
    },
    "EmpJob": {
        "entity_type": "assignment",
        "fields": {
            "userId": "employee_id",  # Lookup
            "position": "position_id",  # Lookup
            "jobCode": "job_id",  # Lookup
            "department": "org_unit_id",  # Lookup
            "managerId": "manager_id",  # Lookup
            "startDate": "start_date",
            "endDate": "end_date",
            "emplStatus": "status",
        }
    },
    "Position": {
        "entity_type": "position",
        "fields": {
            "code": "position_code",
            "externalName_defaultValue": "position_title",
            "externalName_en_US": "position_title",
            "jobCode": "job_id",  # Lookup
            "department": "org_unit_id",  # Lookup
            "parentPosition": "reports_to_position_id",  # Lookup
            "incumbent": "employee_id",  # Lookup
            "type": "position_type",
            "effectiveStartDate": "effective_start_date",
            "effectiveEndDate": "effective_end_date",
        }
    }
}

# Status transformations
STATUS_MAPPINGS = {
    "A": "Active",
    "I": "Inactive",
    "t": "Active",
    "f": "Terminated",
    "active": "Active",
    "inactive": "Inactive",
}
