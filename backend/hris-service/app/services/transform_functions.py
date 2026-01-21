"""
Data transformation functions for field mapping
These functions are applied during data sync to transform HRIS data
"""

from typing import Any, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class TransformFunctions:
    """Collection of transformation functions for field mapping"""
    
    @staticmethod
    def apply_transform(value: Any, transform_function: Optional[str]) -> Any:
        """
        Apply a transformation function to a value
        
        Args:
            value: The source field value
            transform_function: Name of the transform function (e.g., 'uppercase', 'date_format')
        
        Returns:
            Transformed value
        """
        if not transform_function or not value:
            return value
        
        try:
            # Parse function name and parameters
            # Format: "function_name(param1,param2)" or just "function_name"
            if '(' in transform_function:
                func_name = transform_function.split('(')[0].strip()
                params_str = transform_function.split('(')[1].rstrip(')')
                params = [p.strip().strip('"\'') for p in params_str.split(',')] if params_str else []
            else:
                func_name = transform_function.strip()
                params = []
            
            # Get the function
            func = getattr(TransformFunctions, f"transform_{func_name}", None)
            if not func:
                logger.warning(f"Transform function '{func_name}' not found")
                return value
            
            # Apply the function
            if params:
                return func(value, *params)
            else:
                return func(value)
        
        except Exception as e:
            logger.error(f"Error applying transform '{transform_function}': {e}")
            return value
    
    # String transformations
    @staticmethod
    def transform_uppercase(value: str) -> str:
        """Convert string to uppercase"""
        return str(value).upper() if value else value
    
    @staticmethod
    def transform_lowercase(value: str) -> str:
        """Convert string to lowercase"""
        return str(value).lower() if value else value
    
    @staticmethod
    def transform_title_case(value: str) -> str:
        """Convert string to title case"""
        return str(value).title() if value else value
    
    @staticmethod
    def transform_trim(value: str) -> str:
        """Remove leading/trailing whitespace"""
        return str(value).strip() if value else value
    
    @staticmethod
    def transform_replace(value: str, old: str, new: str) -> str:
        """Replace substring in string"""
        return str(value).replace(old, new) if value else value
    
    @staticmethod
    def transform_substring(value: str, start: str, length: str = None) -> str:
        """Extract substring"""
        if not value:
            return value
        start_idx = int(start)
        if length:
            return str(value)[start_idx:int(start_idx) + int(length)]
        return str(value)[start_idx:]
    
    # Date transformations
    @staticmethod
    def transform_date_format(value: Any, format_from: str = "ISO", format_to: str = "YYYY-MM-DD") -> str:
        """
        Convert date format
        format_from: ISO, UNIX_TIMESTAMP, SUCCESSFACTORS
        format_to: YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY, etc.
        """
        if not value:
            return None
        
        try:
            # Parse input date
            if format_from == "ISO" or format_from == "SUCCESSFACTORS":
                # Try ISO format
                if isinstance(value, str):
                    # Handle SuccessFactors date format: "/Date(1234567890)/"
                    if value.startswith("/Date("):
                        timestamp = int(value[6:-2]) / 1000  # Remove /Date( and )/
                        dt = datetime.fromtimestamp(timestamp)
                    else:
                        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                else:
                    dt = value
            elif format_from == "UNIX_TIMESTAMP":
                dt = datetime.fromtimestamp(int(value))
            else:
                dt = datetime.strptime(str(value), format_from)
            
            # Format output
            format_map = {
                "YYYY-MM-DD": "%Y-%m-%d",
                "DD/MM/YYYY": "%d/%m/%Y",
                "MM/DD/YYYY": "%m/%d/%Y",
                "YYYYMMDD": "%Y%m%d"
            }
            
            output_format = format_map.get(format_to, format_to)
            return dt.strftime(output_format)
        
        except Exception as e:
            logger.error(f"Date format error: {e}")
            return str(value)
    
    @staticmethod
    def transform_date_add_days(value: Any, days: str) -> str:
        """Add days to a date"""
        try:
            if isinstance(value, str) and value.startswith("/Date("):
                timestamp = int(value[6:-2]) / 1000
                dt = datetime.fromtimestamp(timestamp)
            else:
                dt = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
            
            from datetime import timedelta
            new_dt = dt + timedelta(days=int(days))
            return new_dt.isoformat()
        except Exception as e:
            logger.error(f"Date add error: {e}")
            return value
    
    # Number transformations
    @staticmethod
    def transform_round(value: Any, decimals: str = "0") -> float:
        """Round number to specified decimal places"""
        try:
            return round(float(value), int(decimals))
        except:
            return value
    
    @staticmethod
    def transform_multiply(value: Any, factor: str) -> float:
        """Multiply number by factor"""
        try:
            return float(value) * float(factor)
        except:
            return value
    
    # Status/Boolean transformations
    @staticmethod
    def transform_status_active(value: Any) -> str:
        """Convert various status values to Active/Inactive"""
        if not value:
            return "Inactive"
        
        value_str = str(value).lower()
        active_values = ["active", "1", "true", "yes", "enabled", "a"]
        return "Active" if value_str in active_values else "Inactive"
    
    @staticmethod
    def transform_boolean(value: Any) -> bool:
        """Convert to boolean"""
        if isinstance(value, bool):
            return value
        value_str = str(value).lower()
        return value_str in ["true", "1", "yes", "y", "active"]
    
    # Null/Default transformations
    @staticmethod
    def transform_default(value: Any, default: str) -> Any:
        """Return default value if source is null/empty"""
        if value is None or value == "":
            return default
        return value
    
    @staticmethod
    def transform_coalesce(value: Any, *alternatives: str) -> Any:
        """Return first non-null value"""
        if value:
            return value
        for alt in alternatives:
            if alt:
                return alt
        return None
    
    @staticmethod
    def transform_constant(value: Any, constant: str) -> Any:
        """
        Always return a constant value, ignoring the source value
        Useful for setting fixed values like status='Active', type='Department', etc.
        
        Args:
            value: Source field value (ignored)
            constant: Constant value to return
        
        Returns:
            The constant value
        """
        return constant
    
    # Custom/Complex transformations
    @staticmethod
    def transform_concat(value: Any, *parts: str) -> str:
        """Concatenate value with additional parts"""
        result = str(value) if value else ""
        for part in parts:
            result += str(part)
        return result
    
    @staticmethod
    def transform_split(value: str, delimiter: str, index: str = "0") -> str:
        """Split string and return specified index"""
        if not value:
            return ""
        parts = str(value).split(delimiter)
        idx = int(index)
        return parts[idx] if idx < len(parts) else ""
    
    # Type/Entity Mapping Transformations
    @staticmethod
    def transform_map_org_unit_type(value: str) -> str:
        """
        Map SuccessFactors org unit type to internal type
        Examples:
        - FOBusinessUnit -> BusinessUnit
        - FODepartment -> Department
        - FODivision -> Division
        - FOCostCenter -> CostCenter
        """
        if not value:
            return "Department"  # Default
        
        value_upper = str(value).upper()
        
        # SuccessFactors to Internal Type Mapping
        type_mapping = {
            "FOLEGALENTITY": "LegalEntity",
            "FOBUSINESSUNIT": "BusinessUnit",
            "FODIVISION": "Division",
            "FODEPARTMENT": "Department",
            "FOCOSTCENTER": "CostCenter",
            "FOTEAM": "Team",
            "FOREGION": "Region",
            "LEGALENTITY": "LegalEntity",
            "BUSINESSUNIT": "BusinessUnit",
            "DIVISION": "Division",
            "DEPARTMENT": "Department",
            "COSTCENTER": "CostCenter",
            "TEAM": "Team",
            "REGION": "Region",
        }
        
        return type_mapping.get(value_upper, "CustomOrgUnit")
    
    @staticmethod
    def transform_map_entity_type(value: str, mapping_dict: str = None) -> str:
        """
        Generic entity type mapping using a dictionary
        Format: map_entity_type('{"A":"Active","I":"Inactive"}')
        """
        if not value:
            return value
        
        # Parse mapping dictionary from string
        import json
        try:
            if mapping_dict:
                mapping = json.loads(mapping_dict)
                return mapping.get(str(value), value)
        except:
            pass
        
        return str(value)

# Available transform functions for UI
AVAILABLE_TRANSFORMS = {
    "String": [
        {"name": "uppercase", "description": "Convert to UPPERCASE", "example": "uppercase"},
        {"name": "lowercase", "description": "Convert to lowercase", "example": "lowercase"},
        {"name": "title_case", "description": "Convert to Title Case", "example": "title_case"},
        {"name": "trim", "description": "Remove whitespace", "example": "trim"},
        {"name": "replace", "description": "Replace text", "example": "replace('old','new')"},
        {"name": "substring", "description": "Extract substring", "example": "substring(0,5)"},
        {"name": "split", "description": "Split and get part", "example": "split(',',0)"},
        {"name": "map_org_unit_type", "description": "Map SF org unit type to internal type", "example": "map_org_unit_type"},
        {"name": "map_entity_type", "description": "Map using custom dictionary", "example": "map_entity_type('{\"A\":\"Active\"}')"},
    ],
    "Date": [
        {"name": "date_format", "description": "Change date format", "example": "date_format('ISO','YYYY-MM-DD')"},
        {"name": "date_add_days", "description": "Add days to date", "example": "date_add_days(30)"},
    ],
    "Number": [
        {"name": "round", "description": "Round number", "example": "round(2)"},
        {"name": "multiply", "description": "Multiply by factor", "example": "multiply(1.5)"},
    ],
    "Status": [
        {"name": "status_active", "description": "Convert to Active/Inactive", "example": "status_active"},
        {"name": "boolean", "description": "Convert to true/false", "example": "boolean"},
        {"name": "map_entity_type", "description": "Map status codes", "example": "map_entity_type('{\"A\":\"Active\"}')"},
    ],
    "Type": [
        {"name": "map_org_unit_type", "description": "Map SF org unit type (FOBusinessUnit → BusinessUnit)", "example": "map_org_unit_type"},
        {"name": "map_entity_type", "description": "Map using custom dictionary", "example": "map_entity_type('{\"FOBusinessUnit\":\"BusinessUnit\"}')"},
    ],
    "Default": [
        {"name": "default", "description": "Use default if empty", "example": "default('N/A')"},
        {"name": "coalesce", "description": "First non-null value", "example": "coalesce('alt1','alt2')"},
        {"name": "constant", "description": "Always return constant value (ignores source)", "example": "constant('Active')"},
    ],
}
