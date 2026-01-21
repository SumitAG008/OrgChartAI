"""
AI Org Structure Generator
Generates and recommends organizational structures
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class OrgStructureGenerator:
    """Generate and recommend organizational structures using AI"""
    
    def __init__(self):
        self.recommendation_history = []
    
    async def generate_org_structure(
        self,
        requirements: Dict[str, Any],
        current_structure: Optional[Dict] = None,
        constraints: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate a recommended organizational structure
        
        Args:
            requirements: {
                "headcount": 100,
                "departments": ["Engineering", "Sales", "Marketing"],
                "hierarchy_levels": 4,
                "span_of_control": 5-8,
                "budget": 5000000
            }
            current_structure: Current org structure (optional)
            constraints: {
                "max_layers": 5,
                "min_span": 3,
                "max_span": 10
            }
        """
        try:
            # Analyze requirements
            analysis = self._analyze_requirements(requirements, constraints)
            
            # Generate structure
            structure = self._generate_structure(analysis)
            
            # Calculate metrics
            metrics = self._calculate_metrics(structure)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(structure, current_structure)
            
            return {
                "structure": structure,
                "metrics": metrics,
                "recommendations": recommendations,
                "analysis": analysis,
                "generated_at": datetime.utcnow().isoformat(),
                "confidence_score": self._calculate_confidence(structure, requirements)
            }
            
        except Exception as e:
            logger.error(f"Error generating org structure: {str(e)}")
            raise
    
    def _analyze_requirements(self, requirements: Dict, constraints: Optional[Dict]) -> Dict:
        """Analyze requirements and constraints"""
        headcount = requirements.get("headcount", 50)
        departments = requirements.get("departments", [])
        hierarchy_levels = requirements.get("hierarchy_levels", 3)
        
        # Calculate optimal structure
        optimal_span = self._calculate_optimal_span(headcount, hierarchy_levels)
        
        return {
            "headcount": headcount,
            "departments": departments,
            "hierarchy_levels": hierarchy_levels,
            "optimal_span": optimal_span,
            "constraints": constraints or {}
        }
    
    def _calculate_optimal_span(self, headcount: int, levels: int) -> float:
        """Calculate optimal span of control"""
        if levels <= 1:
            return headcount
        
        # Use geometric progression
        span = headcount ** (1.0 / (levels - 1))
        return max(3, min(10, round(span, 1)))
    
    def _generate_structure(self, analysis: Dict) -> Dict:
        """Generate the actual org structure"""
        departments = analysis["departments"]
        headcount = analysis["headcount"]
        levels = analysis["hierarchy_levels"]
        optimal_span = analysis["optimal_span"]
        
        structure = {
            "root": {
                "id": "ceo-1",
                "name": "CEO",
                "title": "Chief Executive Officer",
                "level": 0,
                "children": []
            }
        }
        
        # Distribute headcount across departments
        headcount_per_dept = headcount // len(departments) if departments else headcount
        
        # Generate department structures
        for idx, dept in enumerate(departments):
            dept_structure = self._generate_department_structure(
                dept, headcount_per_dept, levels - 1, optimal_span, idx
            )
            structure["root"]["children"].append(dept_structure)
        
        return structure
    
    def _generate_department_structure(
        self, 
        dept_name: str, 
        headcount: int, 
        levels: int, 
        span: float,
        dept_index: int
    ) -> Dict:
        """Generate structure for a department"""
        # Department head
        dept_head = {
            "id": f"dept-{dept_index}-head",
            "name": f"{dept_name} Head",
            "title": f"Head of {dept_name}",
            "level": 1,
            "children": []
        }
        
        if levels > 1 and headcount > span:
            # Calculate number of managers needed
            num_managers = int(headcount / span)
            
            for i in range(num_managers):
                manager = {
                    "id": f"dept-{dept_index}-mgr-{i}",
                    "name": f"{dept_name} Manager {i+1}",
                    "title": f"{dept_name} Manager",
                    "level": 2,
                    "children": []
                }
                
                # Add individual contributors
                team_size = int(headcount / num_managers)
                for j in range(team_size):
                    ic = {
                        "id": f"dept-{dept_index}-ic-{i}-{j}",
                        "name": f"{dept_name} Specialist {j+1}",
                        "title": f"{dept_name} Specialist",
                        "level": 3,
                        "children": None
                    }
                    manager["children"].append(ic)
                
                dept_head["children"].append(manager)
        else:
            # Flat structure - all ICs report to head
            for i in range(headcount):
                ic = {
                    "id": f"dept-{dept_index}-ic-{i}",
                    "name": f"{dept_name} Specialist {i+1}",
                    "title": f"{dept_name} Specialist",
                    "level": 1,
                    "children": None
                }
                dept_head["children"].append(ic)
        
        return dept_head
    
    def _calculate_metrics(self, structure: Dict) -> Dict:
        """Calculate org metrics"""
        def count_nodes(node: Dict) -> int:
            count = 1
            if node.get("children"):
                for child in node["children"]:
                    count += count_nodes(child)
            return count
        
        def count_levels(node: Dict, current: int = 0) -> int:
            max_level = current
            if node.get("children"):
                for child in node["children"]:
                    max_level = max(max_level, count_levels(child, current + 1))
            return max_level
        
        def calculate_span(node: Dict) -> List[int]:
            spans = []
            if node.get("children"):
                spans.append(len(node["children"]))
                for child in node["children"]:
                    spans.extend(calculate_span(child))
            return spans
        
        root = structure["root"]
        total_nodes = count_nodes(root)
        max_levels = count_levels(root)
        spans = calculate_span(root)
        avg_span = sum(spans) / len(spans) if spans else 0
        max_span = max(spans) if spans else 0
        min_span = min(spans) if spans else 0
        
        return {
            "total_positions": total_nodes,
            "hierarchy_levels": max_levels,
            "average_span_of_control": round(avg_span, 2),
            "max_span_of_control": max_span,
            "min_span_of_control": min_span,
            "total_managers": len([s for s in spans if s > 0]),
            "total_individual_contributors": total_nodes - len([s for s in spans if s > 0]) - 1
        }
    
    def _generate_recommendations(
        self, 
        new_structure: Dict, 
        current_structure: Optional[Dict]
    ) -> List[Dict]:
        """Generate recommendations for the structure"""
        recommendations = []
        
        metrics = self._calculate_metrics(new_structure)
        
        # Span of control recommendations
        if metrics["average_span_of_control"] < 3:
            recommendations.append({
                "type": "span_of_control",
                "severity": "warning",
                "message": "Average span of control is too low. Consider consolidating teams.",
                "suggestion": "Increase span to 5-8 for better efficiency"
            })
        elif metrics["average_span_of_control"] > 10:
            recommendations.append({
                "type": "span_of_control",
                "severity": "warning",
                "message": "Average span of control is too high. Managers may be overloaded.",
                "suggestion": "Add intermediate management layers or reduce direct reports"
            })
        
        # Hierarchy depth recommendations
        if metrics["hierarchy_levels"] > 6:
            recommendations.append({
                "type": "hierarchy_depth",
                "severity": "info",
                "message": "Deep hierarchy detected. Consider flattening structure.",
                "suggestion": "Reduce to 4-5 levels for better communication"
            })
        
        # Compare with current structure
        if current_structure:
            current_metrics = self._calculate_metrics(current_structure)
            if metrics["total_positions"] > current_metrics["total_positions"] * 1.2:
                recommendations.append({
                    "type": "headcount_increase",
                    "severity": "info",
                    "message": f"Proposed structure increases headcount by {((metrics['total_positions'] / current_metrics['total_positions'] - 1) * 100):.1f}%",
                    "suggestion": "Review budget and business case for additional positions"
                })
        
        return recommendations
    
    def _calculate_confidence(self, structure: Dict, requirements: Dict) -> float:
        """Calculate confidence score for the generated structure"""
        metrics = self._calculate_metrics(structure)
        target_headcount = requirements.get("headcount", 50)
        
        # Base confidence
        confidence = 0.8
        
        # Adjust based on how well it matches requirements
        if abs(metrics["total_positions"] - target_headcount) / target_headcount < 0.1:
            confidence += 0.1
        
        # Check span of control
        if 5 <= metrics["average_span_of_control"] <= 8:
            confidence += 0.05
        
        return min(1.0, confidence)
    
    async def save_as_draft(
        self,
        structure: Dict,
        name: str,
        description: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Save generated structure as draft"""
        draft = {
            "id": f"draft-{datetime.utcnow().timestamp()}",
            "name": name,
            "description": description,
            "structure": structure,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat(),
            "created_by": user_id,
            "version": 1
        }
        
        # TODO: Save to database
        logger.info(f"Draft saved: {draft['id']}")
        
        return draft
