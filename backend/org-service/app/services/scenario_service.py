"""
Scenario and Change Plan Service
Handles scenario creation, comparison, and change tracking
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
import logging

from app.models_db import Scenario, OrgUnit, Position, Employee
from app.models import Scenario as ScenarioModel, ChangeItem, ScenarioComparison

logger = logging.getLogger(__name__)

class ScenarioService:
    """Service for managing scenarios and comparisons"""
    
    async def create_scenario(
        self,
        db: AsyncSession,
        name: str,
        description: Optional[str],
        tree_id: str,
        base_scenario_id: Optional[UUID],
        created_by: UUID
    ) -> Scenario:
        """Create a new scenario"""
        scenario = Scenario(
            name=name,
            description=description,
            tree_id=tree_id,
            base_scenario_id=base_scenario_id,
            status="Draft",
            created_by=created_by
        )
        db.add(scenario)
        await db.commit()
        await db.refresh(scenario)
        return scenario
    
    async def get_scenarios(
        self,
        db: AsyncSession,
        status: Optional[str] = None
    ) -> List[Scenario]:
        """Get all scenarios, optionally filtered by status"""
        query = select(Scenario)
        if status:
            query = query.where(Scenario.status == status)
        query = query.order_by(Scenario.created_at.desc())
        
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_scenario(
        self,
        db: AsyncSession,
        scenario_id: UUID
    ) -> Optional[Scenario]:
        """Get a specific scenario"""
        result = await db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        return result.scalar_one_or_none()
    
    async def compare_scenarios(
        self,
        db: AsyncSession,
        source_scenario_id: UUID,
        target_scenario_id: UUID
    ) -> ScenarioComparison:
        """Compare two scenarios and identify changes"""
        # Get scenarios
        source_scenario = await self.get_scenario(db, source_scenario_id)
        target_scenario = await self.get_scenario(db, target_scenario_id)
        
        if not source_scenario or not target_scenario:
            raise ValueError("One or both scenarios not found")
        
        # Get org structure for each scenario
        source_org_units = await self._get_org_units_by_tree(db, source_scenario.tree_id)
        target_org_units = await self._get_org_units_by_tree(db, target_scenario.tree_id)
        
        source_positions = await self._get_positions_by_tree(db, source_scenario.tree_id)
        target_positions = await self._get_positions_by_tree(db, target_scenario.tree_id)
        
        # Compare and identify changes
        changes = []
        
        # Compare positions
        changes.extend(self._compare_positions(source_positions, target_positions))
        
        # Compare org units
        changes.extend(self._compare_org_units(source_org_units, target_org_units))
        
        # Build summary
        summary = {
            "added": len([c for c in changes if c.change_type == "added"]),
            "removed": len([c for c in changes if c.change_type == "removed"]),
            "updated": len([c for c in changes if c.change_type == "updated"]),
            "moved": len([c for c in changes if c.change_type == "moved"])
        }
        
        return ScenarioComparison(
            source_scenario_id=source_scenario_id,
            source_scenario_name=source_scenario.name,
            target_scenario_id=target_scenario_id,
            target_scenario_name=target_scenario.name,
            changes=changes,
            summary=summary,
            compared_at=datetime.utcnow()
        )
    
    async def _get_org_units_by_tree(
        self,
        db: AsyncSession,
        tree_id: str
    ) -> List[OrgUnit]:
        """Get all org units for a scenario tree"""
        result = await db.execute(
            select(OrgUnit).where(OrgUnit.tree_id == tree_id)
        )
        return result.scalars().all()
    
    async def _get_positions_by_tree(
        self,
        db: AsyncSession,
        tree_id: str
    ) -> List[Position]:
        """Get all positions for a scenario tree"""
        # Positions are linked via org_unit.tree_id
        result = await db.execute(
            select(Position)
            .join(OrgUnit)
            .where(OrgUnit.tree_id == tree_id)
        )
        return result.scalars().all()
    
    def _compare_positions(
        self,
        source_positions: List[Position],
        target_positions: List[Position]
    ) -> List[ChangeItem]:
        """Compare positions between scenarios"""
        changes = []
        
        # Create maps for quick lookup
        source_map = {p.id: p for p in source_positions}
        target_map = {p.id: p for p in target_positions}
        
        # Find added positions
        for pos_id, pos in target_map.items():
            if pos_id not in source_map:
                changes.append(ChangeItem(
                    change_type="added",
                    entity_type="position",
                    entity_id=pos.id,
                    entity_name=pos.position_title,
                    new_value=self._position_to_dict(pos)
                ))
        
        # Find removed positions
        for pos_id, pos in source_map.items():
            if pos_id not in target_map:
                changes.append(ChangeItem(
                    change_type="removed",
                    entity_type="position",
                    entity_id=pos.id,
                    entity_name=pos.position_title,
                    old_value=self._position_to_dict(pos)
                ))
        
        # Find updated positions
        for pos_id in source_map:
            if pos_id in target_map:
                source_pos = source_map[pos_id]
                target_pos = target_map[pos_id]
                
                field_changes = self._compare_position_fields(source_pos, target_pos)
                if field_changes:
                    changes.append(ChangeItem(
                        change_type="updated",
                        entity_type="position",
                        entity_id=pos_id,
                        entity_name=target_pos.position_title,
                        old_value=self._position_to_dict(source_pos),
                        new_value=self._position_to_dict(target_pos),
                        changes=field_changes
                    ))
                
                # Check if moved (different reports_to or org_unit)
                if (source_pos.reports_to_position_id != target_pos.reports_to_position_id or
                    source_pos.org_unit_id != target_pos.org_unit_id):
                    changes.append(ChangeItem(
                        change_type="moved",
                        entity_type="position",
                        entity_id=pos_id,
                        entity_name=target_pos.position_title,
                        old_value={"reports_to": str(source_pos.reports_to_position_id), "org_unit": str(source_pos.org_unit_id)},
                        new_value={"reports_to": str(target_pos.reports_to_position_id), "org_unit": str(target_pos.org_unit_id)}
                    ))
        
        return changes
    
    def _compare_org_units(
        self,
        source_org_units: List[OrgUnit],
        target_org_units: List[OrgUnit]
    ) -> List[ChangeItem]:
        """Compare org units between scenarios"""
        changes = []
        
        source_map = {ou.id: ou for ou in source_org_units}
        target_map = {ou.id: ou for ou in target_org_units}
        
        # Added
        for ou_id, ou in target_map.items():
            if ou_id not in source_map:
                changes.append(ChangeItem(
                    change_type="added",
                    entity_type="org_unit",
                    entity_id=ou.id,
                    entity_name=ou.name,
                    new_value=self._org_unit_to_dict(ou)
                ))
        
        # Removed
        for ou_id, ou in source_map.items():
            if ou_id not in target_map:
                changes.append(ChangeItem(
                    change_type="removed",
                    entity_type="org_unit",
                    entity_id=ou.id,
                    entity_name=ou.name,
                    old_value=self._org_unit_to_dict(ou)
                ))
        
        # Updated
        for ou_id in source_map:
            if ou_id in target_map:
                source_ou = source_map[ou_id]
                target_ou = target_map[ou_id]
                
                field_changes = self._compare_org_unit_fields(source_ou, target_ou)
                if field_changes:
                    changes.append(ChangeItem(
                        change_type="updated",
                        entity_type="org_unit",
                        entity_id=ou_id,
                        entity_name=target_ou.name,
                        old_value=self._org_unit_to_dict(source_ou),
                        new_value=self._org_unit_to_dict(target_ou),
                        changes=field_changes
                    ))
        
        return changes
    
    def _compare_position_fields(
        self,
        source: Position,
        target: Position
    ) -> Dict[str, Dict[str, Any]]:
        """Compare individual fields of a position"""
        changes = {}
        
        fields_to_compare = [
            "position_title", "position_code", "grade", "level",
            "fte", "is_managerial", "status"
        ]
        
        for field in fields_to_compare:
            source_val = getattr(source, field, None)
            target_val = getattr(target, field, None)
            
            if source_val != target_val:
                changes[field] = {
                    "old": source_val,
                    "new": target_val
                }
        
        return changes
    
    def _compare_org_unit_fields(
        self,
        source: OrgUnit,
        target: OrgUnit
    ) -> Dict[str, Dict[str, Any]]:
        """Compare individual fields of an org unit"""
        changes = {}
        
        fields_to_compare = ["name", "code", "type", "status"]
        
        for field in fields_to_compare:
            source_val = getattr(source, field, None)
            target_val = getattr(target, field, None)
            
            if source_val != target_val:
                changes[field] = {
                    "old": source_val,
                    "new": target_val
                }
        
        return changes
    
    def _position_to_dict(self, position: Position) -> Dict[str, Any]:
        """Convert position to dictionary"""
        return {
            "id": str(position.id),
            "position_code": position.position_code,
            "position_title": position.position_title,
            "grade": position.grade,
            "level": position.level,
            "fte": position.fte,
            "is_managerial": position.is_managerial,
            "status": position.status,
            "org_unit_id": str(position.org_unit_id) if position.org_unit_id else None,
            "reports_to_position_id": str(position.reports_to_position_id) if position.reports_to_position_id else None
        }
    
    def _org_unit_to_dict(self, org_unit: OrgUnit) -> Dict[str, Any]:
        """Convert org unit to dictionary"""
        return {
            "id": str(org_unit.id),
            "code": org_unit.code,
            "name": org_unit.name,
            "type": org_unit.type,
            "status": org_unit.status,
            "parent_org_unit_id": str(org_unit.parent_org_unit_id) if org_unit.parent_org_unit_id else None
        }
    
    async def get_scenario_statistics(
        self,
        db: AsyncSession,
        scenario_id: UUID
    ) -> Dict[str, Any]:
        """Get statistics for a scenario"""
        scenario = await self.get_scenario(db, scenario_id)
        if not scenario:
            raise ValueError("Scenario not found")
        
        org_units = await self._get_org_units_by_tree(db, scenario.tree_id)
        positions = await self._get_positions_by_tree(db, scenario.tree_id)
        
        # Get employees for positions
        position_ids = [p.id for p in positions]
        result = await db.execute(
            select(Employee).where(Employee.position_id.in_(position_ids))
        )
        employees = result.scalars().all()
        
        return {
            "org_units_count": len(org_units),
            "positions_count": len(positions),
            "employees_count": len(employees),
            "vacant_positions": len([p for p in positions if p.status == "Vacant"]),
            "active_positions": len([p for p in positions if p.status == "Active"])
        }
