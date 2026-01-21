"""
Chart Builder Service
Transforms database data into tree structure for React org chart components
"""

from typing import Optional, List
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models import TreeNode, Person
from app.models_db import Position, Employee, OrgUnit

class ChartBuilder:
    """Builds org chart tree structures from database"""
    
    async def build_org_chart(
        self,
        db: AsyncSession,
        org_unit_id: Optional[UUID] = None,
        scenario_id: Optional[str] = None,
        as_of_date: Optional[date] = None,
        max_depth: int = 10
    ) -> TreeNode:
        """
        Build hierarchical org chart tree
        Compatible with react-org-chart and @unicef/react-org-chart
        """
        try:
            # Find root position (no reports_to)
            query = select(Position).where(
                Position.reports_to_position_id.is_(None),
                Position.status == 'Active'
            )
            
            if org_unit_id:
                query = query.join(OrgUnit).where(OrgUnit.id == org_unit_id)
            
            result = await db.execute(query)
            root_positions = result.scalars().all()
            
            if not root_positions:
                # Return mock data if no positions found
                return self._get_mock_org_chart()
            
            # Build tree from root
            root_position = root_positions[0]
            return await self._build_node_tree(
                db,
                root_position.id,
                max_depth=max_depth,
                current_depth=0
            )
        except Exception as e:
            # If database tables don't exist, return mock data
            print(f"Database error (tables may not exist): {e}")
            print("Returning mock org chart data...")
            return self._get_mock_org_chart()
    
    async def _build_node_tree(
        self,
        db: AsyncSession,
        position_id: UUID,
        max_depth: int = 10,
        current_depth: int = 0
    ) -> TreeNode:
        """Recursively build tree node"""
        if current_depth >= max_depth:
            return None
        
        # Get position with employee
        query = select(Position, Employee).outerjoin(
            Employee,
            and_(
                Employee.primary_position_id == Position.id,
                Employee.status == 'Active'
            )
        ).where(Position.id == position_id)
        
        result = await db.execute(query)
        row = result.first()
        
        if not row:
            return None
        
        position, employee = row
        
        # Build person data
        person = Person(
            name=employee.preferred_name or f"{employee.first_name} {employee.last_name}" if employee else "Vacant",
            title=position.position_title,
            avatar=employee.photo_url if employee else None,
            email=employee.email if employee else None,
            employment_type=employee.employment_type if employee else None,
            position_type=position.position_type,
            status=position.status
        )
        
        # Get children positions
        children_query = select(Position).where(
            Position.reports_to_position_id == position_id,
            Position.status == 'Active'
        )
        children_result = await db.execute(children_query)
        children_positions = children_result.scalars().all()
        
        # Build children recursively
        children = []
        for child_position in children_positions:
            child_node = await self._build_node_tree(
                db,
                child_position.id,
                max_depth=max_depth,
                current_depth=current_depth + 1
            )
            if child_node:
                children.append(child_node)
        
        return TreeNode(
            id=str(position.id),
            person=person,
            hasChild=len(children) > 0,
            hasParent=position.reports_to_position_id is not None,
            isHighlight=False,
            children=children if children else None
        )
    
    async def build_flat_chart(
        self,
        db: AsyncSession,
        org_unit_id: Optional[UUID] = None,
        scenario_id: Optional[str] = None
    ) -> List[TreeNode]:
        """Build flat list of all nodes"""
        try:
            # Implementation for flat chart view
            query = select(Position).where(Position.status == 'Active')
            result = await db.execute(query)
            positions = result.scalars().all()
            
            if not positions:
                # Return mock data
                mock_tree = self._get_mock_org_chart()
                return self._flatten_tree(mock_tree)
            
            # Build flat list from positions
            nodes = []
            for position in positions:
                # Get employee if exists
                emp_query = select(Employee).where(
                    Employee.primary_position_id == position.id,
                    Employee.status == 'Active'
                )
                emp_result = await db.execute(emp_query)
                employee = emp_result.scalar_one_or_none()
                
                person = Person(
                    name=employee.preferred_name or f"{employee.first_name} {employee.last_name}" if employee else "Vacant",
                    title=position.position_title,
                    avatar=employee.photo_url if employee else None,
                    email=employee.email if employee else None,
                    employment_type=employee.employment_type if employee else None,
                    position_type=position.position_type,
                    status=position.status
                )
                
                nodes.append(TreeNode(
                    id=str(position.id),
                    person=person,
                    hasChild=False,
                    hasParent=position.reports_to_position_id is not None,
                    isHighlight=False,
                    children=None
                ))
            
            return nodes
        except Exception as e:
            print(f"Database error: {e}")
            mock_tree = self._get_mock_org_chart()
            return self._flatten_tree(mock_tree)
    
    def _get_mock_org_chart(self) -> TreeNode:
        """Return mock org chart data when database is not set up"""
        return TreeNode(
            id="root-1",
            person=Person(
                name="CEO",
                title="Chief Executive Officer",
                avatar=None,
                email="ceo@company.com",
                employment_type="Permanent",
                position_type="Executive",
                status="Active"
            ),
            hasChild=True,
            hasParent=False,
            isHighlight=False,
            children=[
                TreeNode(
                    id="cto-1",
                    person=Person(
                        name="CTO",
                        title="Chief Technology Officer",
                        avatar=None,
                        email="cto@company.com",
                        employment_type="Permanent",
                        position_type="Executive",
                        status="Active"
                    ),
                    hasChild=True,
                    hasParent=True,
                    isHighlight=False,
                    children=[
                        TreeNode(
                            id="vp-eng-1",
                            person=Person(
                                name="VP Engineering",
                                title="Vice President of Engineering",
                                avatar=None,
                                email="vpeng@company.com",
                                employment_type="Permanent",
                                position_type="Management",
                                status="Active"
                            ),
                            hasChild=False,
                            hasParent=True,
                            isHighlight=False,
                            children=None
                        )
                    ]
                ),
                TreeNode(
                    id="ai-agent-1",
                    person=Person(
                        name="AI Agent 'Eve'",
                        title="AI Cross-Functional Integrator",
                        avatar="🤖",
                        email="eve@company.com",
                        employment_type="AI Agent",
                        position_type="AI Agent",
                        status="Active"
                    ),
                    hasChild=False,
                    hasParent=True,
                    isHighlight=False,
                    children=None
                ),
                TreeNode(
                    id="coo-1",
                    person=Person(
                        name="COO",
                        title="Chief Operating Officer",
                        avatar=None,
                        email="coo@company.com",
                        employment_type="Permanent",
                        position_type="Executive",
                        status="Active"
                    ),
                    hasChild=True,
                    hasParent=True,
                    isHighlight=False,
                    children=[
                        TreeNode(
                            id="ops-dir-1",
                            person=Person(
                                name="Operations Director",
                                title="Director of Operations",
                                avatar=None,
                                email="opsdir@company.com",
                                employment_type="Permanent",
                                position_type="Management",
                                status="Active"
                            ),
                            hasChild=False,
                            hasParent=True,
                            isHighlight=False,
                            children=None
                        )
                    ]
                )
            ]
        )
    
    def _flatten_tree(self, node: TreeNode) -> List[TreeNode]:
        """Flatten tree structure to list"""
        result = [node]
        if node.children:
            for child in node.children:
                result.extend(self._flatten_tree(child))
        return result
