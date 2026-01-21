"""
AI Chart Generator Service
Uses AI/ML models and MCP to auto-generate org charts from source data
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from app.services.mcp_client import MCPClient
from app.config import settings

class AIChartGenerator:
    """AI-powered org chart generator"""
    
    def __init__(self):
        self.mcp_client = MCPClient()
    
    async def generate_chart(
        self,
        source_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None,
        model_config_id: Optional[str] = None,
        user_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate org chart from source data using AI
        
        Source data can be:
        - HRIS export (JSON/CSV)
        - Manual input
        - Existing org structure
        """
        # Step 1: Analyze source data
        analysis = await self._analyze_source_data(source_data)
        
        # Step 2: Generate org structure using AI
        org_structure = await self._generate_structure_with_ai(
            analysis,
            preferences=preferences,
            model_config_id=model_config_id
        )
        
        # Step 3: Build visualization tree
        chart_tree = await self._build_chart_tree(org_structure)
        
        # Step 4: Calculate confidence score
        confidence = self._calculate_confidence(analysis, org_structure)
        
        # Step 5: Save to database
        chart_id = str(uuid4())
        # TODO: Save to auto_generated_chart table
        
        return {
            "id": chart_id,
            "chart": chart_tree,
            "confidence_score": confidence,
            "model_name": "gpt-4-turbo",  # or from config
            "analysis": analysis
        }
    
    async def _analyze_source_data(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze source data to understand structure"""
        # Use MCP to analyze data
        prompt = f"""
        Analyze this organizational data and identify:
        1. Hierarchy levels
        2. Reporting relationships
        3. Department/function groupings
        4. Key roles and positions
        
        Data: {json.dumps(source_data, indent=2)}
        
        Return JSON with analysis.
        """
        
        response = await self.mcp_client.generate(
            prompt,
            model="gpt-4-turbo",
            context={"task": "org_data_analysis"}
        )
        
        return json.loads(response.get("content", "{}"))
    
    async def _generate_structure_with_ai(
        self,
        analysis: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None,
        model_config_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate org structure using AI model"""
        
        prompt = f"""
        Generate an optimal organizational structure based on this analysis:
        
        Analysis: {json.dumps(analysis, indent=2)}
        
        Preferences: {json.dumps(preferences or {}, indent=2)}
        
        Create a complete org structure with:
        - Org units (divisions, departments, teams)
        - Positions with reporting lines
        - Job profiles
        - Recommended hierarchy depth
        
        Return as JSON matching this schema:
        {{
            "org_units": [...],
            "positions": [...],
            "jobs": [...],
            "hierarchy": {{...}}
        }}
        """
        
        response = await self.mcp_client.generate(
            prompt,
            model="gpt-4-turbo",
            context={"task": "org_structure_generation"}
        )
        
        return json.loads(response.get("content", "{}"))
    
    async def _build_chart_tree(self, org_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Build visualization tree from org structure"""
        # Transform AI-generated structure to chart tree format
        # Compatible with react-org-chart
        
        positions = org_structure.get("positions", [])
        hierarchy = org_structure.get("hierarchy", {})
        
        # Find root position
        root_positions = [p for p in positions if not p.get("reports_to")]
        
        if not root_positions:
            return {"error": "No root position found"}
        
        root = root_positions[0]
        
        # Build tree recursively
        def build_node(position: Dict) -> Dict:
            children_positions = [
                p for p in positions 
                if p.get("reports_to") == position.get("id")
            ]
            
            return {
                "id": position.get("id"),
                "person": {
                    "name": position.get("title", "Position"),
                    "title": position.get("title"),
                    "avatar": "👤"
                },
                "hasChild": len(children_positions) > 0,
                "hasParent": position.get("reports_to") is not None,
                "children": [build_node(child) for child in children_positions] if children_positions else None
            }
        
        return build_node(root)
    
    def _calculate_confidence(
        self,
        analysis: Dict[str, Any],
        org_structure: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for generated chart"""
        # Factors:
        # - Data completeness
        # - Structure coherence
        # - Hierarchy depth
        # - Position coverage
        
        data_completeness = analysis.get("completeness_score", 0.5)
        structure_coherence = 0.8  # Can be calculated from structure
        
        confidence = (data_completeness + structure_coherence) / 2
        return round(confidence, 2)
    
    async def list_generated_charts(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """List all generated charts"""
        # TODO: Query auto_generated_chart table
        return []
    
    async def get_generated_chart(
        self,
        db: AsyncSession,
        chart_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific generated chart"""
        # TODO: Query auto_generated_chart table
        return None
    
    async def approve_chart(
        self,
        db: AsyncSession,
        chart_id: str,
        user_id: str
    ) -> bool:
        """Approve a generated chart"""
        # TODO: Update status to 'Approved'
        return True
    
    async def recommend_team(
        self,
        db: AsyncSession,
        project_requirements: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Recommend team formation using AI"""
        prompt = f"""
        Recommend an optimal team composition for this project:
        
        Requirements: {json.dumps(project_requirements, indent=2)}
        
        Consider:
        - Required skills
        - Team size
        - Budget constraints
        - Availability
        - Past collaboration success
        
        Return JSON with recommended team members and reasoning.
        """
        
        response = await self.mcp_client.generate(
            prompt,
            model="gpt-4-turbo",
            context={"task": "team_formation"}
        )
        
        return json.loads(response.get("content", "{}"))
    
    async def recommend_org_design(
        self,
        db: AsyncSession,
        current_org: Dict[str, Any],
        objectives: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Recommend org design improvements using AI"""
        prompt = f"""
        Analyze this organizational structure and recommend improvements:
        
        Current Org: {json.dumps(current_org, indent=2)}
        Objectives: {json.dumps(objectives, indent=2)}
        
        Consider:
        - Span of control optimization
        - Hierarchy depth
        - Communication efficiency
        - Cost optimization
        
        Return JSON with recommendations and expected impact.
        """
        
        response = await self.mcp_client.generate(
            prompt,
            model="gpt-4-turbo",
            context={"task": "org_design"}
        )
        
        return json.loads(response.get("content", "{}"))
