"""
AI-Powered Field Matching Service
Uses NLP and ML to automatically match HRIS fields to internal schema
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class FieldMatcherAI:
    """AI-powered field matching using semantic similarity"""
    
    def __init__(self):
        self.target_schema = self._load_target_schema()
        self.mapping_history = []
        # TODO: Initialize NLP model (BERT, Sentence Transformers)
        # self.model = AutoModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
        # self.tokenizer = AutoTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
    
    def _load_target_schema(self) -> Dict[str, Dict]:
        """Load target schema with field descriptions"""
        return {
            # Org Unit fields
            "name": {
                "description": "Organizational unit name",
                "type": "string",
                "category": "org_unit"
            },
            "code": {
                "description": "Organizational unit code or identifier",
                "type": "string",
                "category": "org_unit"
            },
            "type": {
                "description": "Type of organizational unit (Department, Division, Team)",
                "type": "enum",
                "category": "org_unit"
            },
            "parent_org_unit_id": {
                "description": "Parent organizational unit reference",
                "type": "reference",
                "category": "org_unit"
            },
            "status": {
                "description": "Active or inactive status",
                "type": "enum",
                "category": "org_unit"
            },
            # Position fields
            "position_code": {
                "description": "Position identifier code",
                "type": "string",
                "category": "position"
            },
            "position_title": {
                "description": "Job title or position name",
                "type": "string",
                "category": "position"
            },
            "reports_to_position_id": {
                "description": "Manager position reference",
                "type": "reference",
                "category": "position"
            },
            "org_unit_id": {
                "description": "Organizational unit this position belongs to",
                "type": "reference",
                "category": "position"
            },
            # Employee fields
            "employee_number": {
                "description": "Unique employee identifier",
                "type": "string",
                "category": "employee"
            },
            "first_name": {
                "description": "Employee's first name",
                "type": "string",
                "category": "employee"
            },
            "last_name": {
                "description": "Employee's last name",
                "type": "string",
                "category": "employee"
            },
            "preferred_name": {
                "description": "Display name or preferred name",
                "type": "string",
                "category": "employee"
            },
            "email": {
                "description": "Email address",
                "type": "email",
                "category": "employee"
            },
            "position_id": {
                "description": "Current position assignment",
                "type": "reference",
                "category": "employee"
            }
        }
    
    def find_best_match(
        self, 
        source_field: str, 
        source_type: str = "string",
        context: str = "",
        category: Optional[str] = None
    ) -> Dict:
        """
        Find best matching target field using semantic similarity
        
        Args:
            source_field: Field name from HRIS (e.g., "orgUnitName")
            source_type: Field type (string, number, date, reference)
            context: Additional context about the field
            category: Entity category (org_unit, position, employee)
        
        Returns:
            {
                "best_match": "name",
                "confidence": 0.95,
                "alternatives": [...],
                "reason": "Semantic similarity match"
            }
        """
        # Filter target fields by category if provided
        candidate_fields = self.target_schema
        if category:
            candidate_fields = {
                k: v for k, v in candidate_fields.items()
                if v.get("category") == category
            }
        
        # Simple keyword-based matching (Phase 1)
        # TODO: Replace with NLP model in Phase 2
        best_match = None
        best_score = 0.0
        alternatives = []
        
        source_lower = source_field.lower()
        
        for target_field, target_info in candidate_fields.items():
            score = self._calculate_similarity(
                source_field, 
                source_lower,
                target_field,
                target_info,
                source_type,
                context
            )
            
            if score > best_score:
                if best_match:
                    alternatives.append({
                        "field": best_match["field"],
                        "confidence": best_match["confidence"]
                    })
                best_match = {
                    "field": target_field,
                    "confidence": score,
                    "description": target_info["description"]
                }
                best_score = score
            elif score > 0.5:
                alternatives.append({
                    "field": target_field,
                    "confidence": score,
                    "description": target_info["description"]
                })
        
        return {
            "best_match": best_match["field"] if best_match else None,
            "confidence": best_match["confidence"] if best_match else 0.0,
            "alternatives": sorted(alternatives, key=lambda x: x["confidence"], reverse=True)[:3],
            "reason": self._generate_reason(source_field, best_match, source_type) if best_match else "No match found"
        }
    
    def _calculate_similarity(
        self,
        source_field: str,
        source_lower: str,
        target_field: str,
        target_info: Dict,
        source_type: str,
        context: str
    ) -> float:
        """Calculate similarity score between source and target fields"""
        score = 0.0
        
        target_lower = target_field.lower()
        target_desc_lower = target_info["description"].lower()
        
        # Exact match
        if source_lower == target_lower:
            return 1.0
        
        # Partial match in field name
        if target_lower in source_lower or source_lower in target_lower:
            score += 0.4
        
        # Keyword matching
        keywords = {
            "name": ["name", "title", "label"],
            "code": ["code", "id", "identifier", "key"],
            "type": ["type", "category", "kind"],
            "parent": ["parent", "superior", "manager", "reports"],
            "status": ["status", "state", "active"],
            "email": ["email", "mail", "e-mail"],
            "first": ["first", "given", "forename"],
            "last": ["last", "surname", "family"],
            "number": ["number", "num", "id", "identifier"],
            "title": ["title", "position", "role", "job"]
        }
        
        for keyword, variations in keywords.items():
            if keyword in target_lower:
                for variation in variations:
                    if variation in source_lower:
                        score += 0.3
                        break
        
        # Type matching
        if source_type == target_info.get("type"):
            score += 0.2
        
        # Description matching
        for word in source_lower.split():
            if len(word) > 3 and word in target_desc_lower:
                score += 0.1
        
        return min(1.0, score)
    
    def _generate_reason(
        self, 
        source_field: str, 
        best_match: Dict, 
        source_type: str
    ) -> str:
        """Generate human-readable reason for the match"""
        if best_match["confidence"] > 0.9:
            return f"High confidence match: '{source_field}' semantically matches '{best_match['field']}'"
        elif best_match["confidence"] > 0.7:
            return f"Good match: '{source_field}' is similar to '{best_match['field']}'"
        else:
            return f"Moderate match: '{source_field}' may map to '{best_match['field']}' (review recommended)"
    
    def discover_schema_mappings(
        self, 
        source_schema: Dict[str, Dict],
        entity_category: str
    ) -> Dict[str, Dict]:
        """
        Discover mappings for an entire schema
        
        Args:
            source_schema: {
                "orgUnitName": {"type": "string", "description": "..."},
                "orgUnitCode": {"type": "string", "description": "..."},
                ...
            }
            entity_category: "org_unit", "position", or "employee"
        
        Returns:
            {
                "orgUnitName": {
                    "best_match": "name",
                    "confidence": 0.95,
                    "alternatives": [...]
                },
                ...
            }
        """
        mappings = {}
        
        for source_field, field_info in source_schema.items():
            match_result = self.find_best_match(
                source_field=source_field,
                source_type=field_info.get("type", "string"),
                context=field_info.get("description", ""),
                category=entity_category
            )
            mappings[source_field] = match_result
        
        return mappings
    
    def learn_from_correction(
        self,
        source_field: str,
        ai_suggestion: str,
        user_correction: str,
        context: Optional[Dict] = None
    ):
        """Learn from user corrections to improve future mappings"""
        self.mapping_history.append({
            "source_field": source_field,
            "ai_suggestion": ai_suggestion,
            "user_correction": user_correction,
            "context": context or {},
            "timestamp": str(datetime.utcnow())
        })
        
        # TODO: Retrain model or update weights based on corrections
        logger.info(f"Learned correction: {source_field} -> {user_correction} (AI suggested: {ai_suggestion})")
    
    def get_mapping_suggestions(
        self,
        source_fields: List[str],
        entity_category: str
    ) -> Dict[str, Dict]:
        """Get mapping suggestions for multiple fields at once"""
        suggestions = {}
        
        for field in source_fields:
            suggestions[field] = self.find_best_match(
                source_field=field,
                category=entity_category
            )
        
        return suggestions
