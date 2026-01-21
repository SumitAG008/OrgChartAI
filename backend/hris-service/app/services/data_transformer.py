"""
Transform HRIS data to our internal data model
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.successfactors_client import (
    SuccessFactorsUser, SuccessFactorsPosition, SuccessFactorsOrgUnit
)
from app.services.hierarchy_resolver import HierarchyResolver
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class DataTransformer:
    """Transform HRIS data to internal format"""
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.hierarchy_resolver = HierarchyResolver(db) if db else None
    
    @staticmethod
    def transform_successfactors_user(user: SuccessFactorsUser) -> Dict[str, Any]:
        """Transform SuccessFactors user to employee format"""
        return {
            "employee_number": user.custom01 or user.userId,
            "first_name": user.firstName or "",
            "last_name": user.lastName or "",
            "preferred_name": user.displayName or f"{user.firstName} {user.lastName}",
            "email": user.email,
            "status": "Active" if user.status == "active" else "Inactive",
            "hris_id": user.userId,
            "hris_source": "successfactors"
        }
    
    @staticmethod
    def transform_successfactors_position(position: SuccessFactorsPosition) -> Dict[str, Any]:
        """Transform SuccessFactors position to position format"""
        return {
            "position_code": position.positionCode or position.positionId,
            "position_title": position.positionTitle or "",
            "status": "Active" if position.status == "active" else "Vacant",
            "hris_id": position.positionId,
            "hris_source": "successfactors",
            "reports_to_hris_id": position.reportsToPositionId
        }
    
    async def transform_successfactors_org_unit(
        self, 
        org_unit: SuccessFactorsOrgUnit,
        entity_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transform SuccessFactors org unit to org_unit format
        Uses hierarchy resolver to determine proper type and level
        """
        # Get parent HRIS ID
        parent_hris_id = org_unit.parentOrgUnitId
        
        # Determine type (level is calculated from relationships)
        if self.hierarchy_resolver:
            # Try to get type from entity name (e.g., "FOBusinessUnit", "FODepartment")
            hris_type = org_unit.orgUnitType or entity_name
            
            internal_type, _ = await self.hierarchy_resolver.determine_org_unit_type(
                "successfactors",
                hris_type,
                entity_name
            )
            
            # Resolve parent if exists
            parent_info = None
            if parent_hris_id:
                parent_info = await self.hierarchy_resolver.resolve_parent_org_unit(
                    parent_hris_id,
                    "successfactors",
                    internal_type
                )
            
            # Calculate hierarchy level from actual parent relationship
            hierarchy_level = await self.hierarchy_resolver.calculate_hierarchy_level(
                None,  # org_unit_id not available yet
                parent_hris_id,
                "successfactors"
            )
        else:
            # Fallback without hierarchy resolver
            internal_type = org_unit.orgUnitType or "Department"
            hierarchy_level = 1  # Default to level 1, will be recalculated
            parent_info = None
            logger.warning("Hierarchy resolver not available, using defaults")
        
        return {
            "code": org_unit.orgUnitCode or org_unit.orgUnitId,
            "name": org_unit.orgUnitName or "",
            "type": internal_type,
            "hierarchy_level": hierarchy_level,
            "status": "Active" if org_unit.status == "active" else "Inactive",
            "hris_id": org_unit.orgUnitId,
            "hris_source": "successfactors",
            "hris_type": org_unit.orgUnitType or entity_name,  # Store original HRIS type
            "parent_hris_id": parent_hris_id,
            "parent_org_unit_id": parent_info["id"] if parent_info else None,
            "parent_info": parent_info
        }
    
    @staticmethod
    def transform_users(users: List[SuccessFactorsUser]) -> List[Dict[str, Any]]:
        """Transform list of users"""
        return [DataTransformer.transform_successfactors_user(user) for user in users]
    
    @staticmethod
    def transform_positions(positions: List[SuccessFactorsPosition]) -> List[Dict[str, Any]]:
        """Transform list of positions"""
        return [DataTransformer.transform_successfactors_position(pos) for pos in positions]
    
    @staticmethod
    def transform_org_units(org_units: List[SuccessFactorsOrgUnit]) -> List[Dict[str, Any]]:
        """Transform list of org units"""
        return [DataTransformer.transform_successfactors_org_unit(ou) for ou in org_units]
