"""
Hierarchy Resolution Service
Determines org unit types, hierarchy levels, and parent-child relationships
"""

from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
import logging

logger = logging.getLogger(__name__)


class HierarchyResolver:
    """Resolves org unit hierarchy, types, and parent-child relationships"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def map_hris_type_to_internal(
        self, 
        hris_source: str, 
        hris_type: str
    ) -> Tuple[str, Optional[int]]:
        """
        Map HRIS org unit type to internal type
        Hierarchy level is calculated from actual parent-child relationships, not fixed
        
        Args:
            hris_source: HRIS system name (e.g., 'successfactors')
            hris_type: Original type from HRIS (e.g., 'FOBusinessUnit', 'FODepartment')
        
        Returns:
            Tuple of (internal_type, hierarchy_level)
            hierarchy_level is None if level should be calculated from relationships
        """
        try:
            query = text("""
                SELECT internal_type, hierarchy_level
                FROM hris_org_unit_type_mapping
                WHERE hris_source = :hris_source
                AND hris_type = :hris_type
                AND is_active = TRUE
            """)
            result = await self.db.execute(
                query, 
                {"hris_source": hris_source, "hris_type": hris_type}
            )
            row = result.fetchone()
            
            if row:
                # hierarchy_level can be NULL (flexible) or a fixed value
                return (row[0], row[1])
            
            # Default fallback
            logger.warning(
                f"No mapping found for {hris_source}.{hris_type}, "
                f"defaulting to Department"
            )
            return ("Department", None)  # No fixed level
            
        except Exception as e:
            logger.error(f"Error mapping HRIS type: {e}")
            return ("Department", None)  # No fixed level
    
    async def is_valid_parent_child(
        self, 
        parent_type: str, 
        child_type: str
    ) -> bool:
        """
        Check if parent-child relationship is valid based on hierarchy rules
        
        Args:
            parent_type: Internal type of parent org unit
            child_type: Internal type of child org unit
        
        Returns:
            True if relationship is valid, False otherwise
        """
        try:
            query = text("""
                SELECT EXISTS(
                    SELECT 1
                    FROM org_unit_type_hierarchy
                    WHERE parent_type = :parent_type
                    AND child_type = :child_type
                    AND is_allowed = TRUE
                )
            """)
            result = await self.db.execute(
                query,
                {"parent_type": parent_type, "child_type": child_type}
            )
            return result.scalar() or False
            
        except Exception as e:
            logger.error(f"Error validating parent-child: {e}")
            return True  # Allow by default if validation fails
    
    async def resolve_parent_org_unit(
        self,
        parent_hris_id: Optional[str],
        hris_source: str,
        child_type: str
    ) -> Optional[Dict]:
        """
        Resolve parent org unit by HRIS ID and validate relationship
        
        Args:
            parent_hris_id: HRIS ID of parent org unit
            hris_source: HRIS system name
            child_type: Type of child org unit
        
        Returns:
            Dict with parent org unit info or None
        """
        if not parent_hris_id:
            return None
        
        try:
            # Find parent by HRIS ID
            query = text("""
                SELECT id, type, hierarchy_level, code, name
                FROM org_unit
                WHERE hris_id = :parent_hris_id
                AND hris_source = :hris_source
            """)
            result = await self.db.execute(
                query,
                {"parent_hris_id": parent_hris_id, "hris_source": hris_source}
            )
            parent = result.fetchone()
            
            if not parent:
                logger.warning(
                    f"Parent org unit not found: {parent_hris_id} "
                    f"from {hris_source}"
                )
                return None
            
            # Validate relationship
            is_valid = await self.is_valid_parent_child(parent[1], child_type)
            
            if not is_valid:
                logger.warning(
                    f"Invalid parent-child relationship: "
                    f"{parent[1]} -> {child_type}"
                )
                # Still return parent, but log warning
                # User can override if needed
            
            return {
                "id": str(parent[0]),
                "type": parent[1],
                "hierarchy_level": parent[2],
                "code": parent[3],
                "name": parent[4]
            }
            
        except Exception as e:
            logger.error(f"Error resolving parent org unit: {e}")
            return None
    
    async def determine_org_unit_type(
        self,
        hris_source: str,
        hris_type: Optional[str],
        hris_entity_name: Optional[str] = None
    ) -> Tuple[str, Optional[int]]:
        """
        Determine org unit type from HRIS data
        Hierarchy level is calculated from actual relationships, not fixed
        
        Args:
            hris_source: HRIS system name
            hris_type: Type from HRIS (e.g., 'FOBusinessUnit')
            hris_entity_name: Entity name from HRIS (e.g., 'FOBusinessUnit', 'FODepartment')
        
        Returns:
            Tuple of (internal_type, hierarchy_level)
            hierarchy_level is None if level should be calculated from parent relationships
        """
        # Try to get type from entity name if hris_type is not provided
        if not hris_type and hris_entity_name:
            # Extract type from entity name
            # e.g., "FOBusinessUnit" -> "FOBusinessUnit"
            hris_type = hris_entity_name
        
        if hris_type:
            return await self.map_hris_type_to_internal(hris_source, hris_type)
        
        # Default fallback
        logger.warning(
            f"Could not determine org unit type for {hris_source}, "
            f"defaulting to Department"
        )
        return ("Department", None)  # No fixed level
    
    async def calculate_hierarchy_level(
        self,
        org_unit_id: Optional[str],
        parent_hris_id: Optional[str],
        hris_source: str
    ) -> int:
        """
        Calculate hierarchy level from actual parent-child relationships
        Traverses up the hierarchy to count levels
        
        Args:
            org_unit_id: Internal UUID of org unit (if already exists)
            parent_hris_id: HRIS ID of parent
            hris_source: HRIS system name
        
        Returns:
            Hierarchy level (1 = top, 2 = second, etc.)
        """
        try:
            # If we have the org_unit_id, use the database function
            if org_unit_id:
                query = text("SELECT calculate_org_unit_level(:org_unit_id::uuid)")
                result = await self.db.execute(query, {"org_unit_id": org_unit_id})
                level = result.scalar()
                if level:
                    return level
            
            # Otherwise, calculate from parent
            if parent_hris_id:
                # Find parent and calculate its level + 1
                query = text("""
                    SELECT calculate_org_unit_level(id)
                    FROM org_unit
                    WHERE hris_id = :parent_hris_id
                    AND hris_source = :hris_source
                """)
                result = await self.db.execute(
                    query,
                    {"parent_hris_id": parent_hris_id, "hris_source": hris_source}
                )
                parent_level = result.scalar()
                if parent_level:
                    return parent_level + 1
            
            # No parent = top level
            return 1
            
        except Exception as e:
            logger.error(f"Error calculating hierarchy level: {e}")
            return 1  # Default to level 1
    
    async def build_org_unit_hierarchy(
        self,
        org_units: List[Dict],
        hris_source: str
    ) -> List[Dict]:
        """
        Build org unit hierarchy with proper types and parent relationships
        
        Args:
            org_units: List of org unit dicts from HRIS
            hris_source: HRIS system name
        
        Returns:
            List of org units with resolved types, levels, and parent relationships
        """
        resolved_units = []
        
        for unit in org_units:
            # Determine type and hierarchy level
            hris_type = unit.get('hris_type') or unit.get('type')
            entity_name = unit.get('entity_name')
            
            internal_type, hierarchy_level = await self.determine_org_unit_type(
                hris_source,
                hris_type,
                entity_name
            )
            
            # Resolve parent
            parent_hris_id = unit.get('parent_hris_id') or unit.get('parentOrgUnitId')
            parent_info = None
            
            if parent_hris_id:
                parent_info = await self.resolve_parent_org_unit(
                    parent_hris_id,
                    hris_source,
                    internal_type
                )
            
            # Build resolved unit
            resolved_unit = {
                **unit,
                "type": internal_type,
                "hierarchy_level": hierarchy_level,
                "hris_type": hris_type,
                "parent_info": parent_info,
                "parent_org_unit_id": parent_info["id"] if parent_info else None
            }
            
            resolved_units.append(resolved_unit)
        
        return resolved_units
