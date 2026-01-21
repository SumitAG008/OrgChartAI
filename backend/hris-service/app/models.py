"""
Pydantic models for HRIS service
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class HRISSystem(str, Enum):
    SUCCESSFACTORS = "successfactors"
    WORKDAY = "workday"
    BAMBOOHR = "bamboohr"
    ADP = "adp"
    ORACLE_HCM = "oracle_hcm"
    CSV = "csv"

class ConnectionStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"

class SyncStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

# Connection Models
class HRISConnectionBase(BaseModel):
    name: str
    system: HRISSystem
    description: Optional[str] = None
    is_active: bool = True

class HRISConnectionCreate(HRISConnectionBase):
    credentials: Dict[str, Any]  # Encrypted credentials

class HRISConnectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    credentials: Optional[Dict[str, Any]] = None

class HRISConnection(HRISConnectionBase):
    id: str
    status: ConnectionStatus
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[SyncStatus] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# SuccessFactors Models
class SuccessFactorsCredentials(BaseModel):
    company_id: str
    username: str
    password: str
    api_url: Optional[str] = None  # e.g., "https://api.successfactors.eu"

class SuccessFactorsConnectionTest(BaseModel):
    success: bool
    message: str
    api_version: Optional[str] = None

# Sync Models
class SyncRequest(BaseModel):
    connection_id: str
    sync_type: str = "full"  # full, incremental
    entities: Optional[List[str]] = None  # ["employees", "positions", "org_units"]

class SyncResponse(BaseModel):
    sync_id: str
    status: SyncStatus
    started_at: datetime
    connection_id: str
    entities: List[str]
    total_records: Optional[int] = None
    processed_records: Optional[int] = None
    failed_records: Optional[int] = None
    errors: Optional[List[str]] = None

class SyncProgress(BaseModel):
    sync_id: str
    status: SyncStatus
    progress_percentage: float
    current_entity: Optional[str] = None
    processed: int
    total: int
    errors: List[str]

# Data Models (from SuccessFactors)
class SuccessFactorsUser(BaseModel):
    """SuccessFactors User (Employee) data"""
    userId: str
    username: Optional[str] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    middleName: Optional[str] = None
    displayName: Optional[str] = None
    status: Optional[str] = None  # active, inactive
    custom01: Optional[str] = None  # employee number
    custom02: Optional[str] = None
    # Add more fields as needed

class SuccessFactorsPosition(BaseModel):
    """SuccessFactors Position data"""
    positionId: str
    positionCode: Optional[str] = None
    positionTitle: Optional[str] = None
    jobCode: Optional[str] = None
    department: Optional[str] = None
    division: Optional[str] = None
    reportsToPositionId: Optional[str] = None
    status: Optional[str] = None
    # Add more fields as needed

class SuccessFactorsOrgUnit(BaseModel):
    """SuccessFactors Organizational Unit data"""
    orgUnitId: str
    orgUnitCode: Optional[str] = None
    orgUnitName: Optional[str] = None
    parentOrgUnitId: Optional[str] = None
    orgUnitType: Optional[str] = None
    status: Optional[str] = None
    # Add more fields as needed
