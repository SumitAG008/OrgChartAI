"""
SuccessFactors $metadata Parser
Parses OData $metadata XML to extract entities and fields
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# OData namespaces
EDM_NS = {
    'edmx': 'http://schemas.microsoft.com/ado/2007/06/edmx',
    'edm': 'http://schemas.microsoft.com/ado/2008/09/edm',
    'edmx_data': 'http://schemas.microsoft.com/ado/2007/06/edmx',
    'edm_data': 'http://schemas.microsoft.com/ado/2008/09/edm'
}

class MetadataParser:
    """Parse SuccessFactors OData $metadata XML"""
    
    def __init__(self, metadata_xml: str):
        self.metadata_xml = metadata_xml
        try:
            self.root = ET.fromstring(metadata_xml)
        except ET.ParseError as e:
            logger.error(f"Error parsing XML: {e}")
            raise ValueError(f"Invalid XML metadata: {e}")
    
    def get_all_entities(self) -> List[Dict[str, Any]]:
        """Extract all EntityTypes from metadata"""
        entities = []
        
        # Try different namespace patterns (SuccessFactors may use different namespaces)
        namespaces = [
            '{http://schemas.microsoft.com/ado/2008/09/edm}',
            '{http://schemas.microsoft.com/ado/2007/05/edm}',
            ''  # No namespace
        ]
        
        entity_types = []
        for ns in namespaces:
            entity_types = self.root.findall(f'.//{ns}EntityType')
            if entity_types:
                break
        
        # If still not found, try without namespace prefix
        if not entity_types:
            entity_types = self.root.findall('.//EntityType')
        
        for entity_type in entity_types:
            entity_name = entity_type.get('Name')
            if not entity_name:
                continue
            
            # Get properties count (try different namespaces)
            properties = []
            for ns in namespaces:
                properties = entity_type.findall(f'.//{ns}Property')
                if properties:
                    break
            if not properties:
                properties = entity_type.findall('.//Property')
            
            properties_count = len(properties)
            
            # Try to find description or documentation
            documentation = None
            for ns in namespaces:
                documentation = entity_type.find(f'.//{ns}Documentation')
                if documentation is not None:
                    break
            if documentation is None:
                documentation = entity_type.find('.//Documentation')
            
            description = documentation.text if documentation is not None and documentation.text else None
            
            # Check if it's a navigation property (relationship)
            navigation_properties = []
            for ns in namespaces:
                navigation_properties = entity_type.findall(f'.//{ns}NavigationProperty')
                if navigation_properties:
                    break
            if not navigation_properties:
                navigation_properties = entity_type.findall('.//NavigationProperty')
            
            entities.append({
                'name': entity_name,
                'display_name': self._format_display_name(entity_name),
                'description': description or f"{entity_name} entity from SuccessFactors",
                'fields_count': properties_count,
                'has_navigation': len(navigation_properties) > 0,
                'is_complex': entity_type.get('BaseType') is not None
            })
        
        return sorted(entities, key=lambda x: x['name'])
    
    def get_entity_fields(self, entity_name: str) -> List[Dict[str, Any]]:
        """Get all fields/properties for a specific entity"""
        fields = []
        
        # Try different namespace patterns
        namespaces = [
            '{http://schemas.microsoft.com/ado/2008/09/edm}',
            '{http://schemas.microsoft.com/ado/2007/05/edm}',
            ''  # No namespace
        ]
        
        # Find the EntityType
        entity_type = None
        for ns in namespaces:
            entity_type = self.root.find(f'.//{ns}EntityType[@Name="{entity_name}"]')
            if entity_type is not None:
                break
        
        if entity_type is None:
            # Try without namespace
            entity_type = self.root.find(f'.//EntityType[@Name="{entity_name}"]')
        
        if entity_type is None:
            return fields
        
        # Get all Property elements (try different namespaces)
        properties = []
        for ns in namespaces:
            properties = entity_type.findall(f'.//{ns}Property')
            if properties:
                break
        if not properties:
            properties = entity_type.findall('.//Property')
        
        for prop in properties:
            field_name = prop.get('Name')
            if not field_name:
                continue
                
            field_type = prop.get('Type', 'String')
            nullable_str = prop.get('Nullable', 'true')
            nullable = nullable_str.lower() == 'true' if nullable_str else True
            
            # Get documentation if available
            documentation = None
            for ns in namespaces:
                documentation = prop.find(f'.//{ns}Documentation')
                if documentation is not None:
                    break
            if documentation is None:
                documentation = prop.find('.//Documentation')
            
            description = documentation.text if documentation is not None and documentation.text else None
            
            # Clean up type name (remove namespace)
            if '.' in field_type:
                field_type = field_type.split('.')[-1]
            # Remove Edm. prefix if present
            if field_type.startswith('Edm.'):
                field_type = field_type[4:]
            
            # Ensure type is not empty - default to String if empty
            if not field_type or field_type.strip() == '':
                field_type = 'String'
            
            fields.append({
                'name': field_name,
                'type': field_type,
                'nullable': nullable,
                'description': description
            })
        
        return sorted(fields, key=lambda x: x['name'])
    
    def _format_display_name(self, entity_name: str) -> str:
        """Format entity name for display"""
        # Convert camelCase to Title Case
        import re
        # Insert space before capital letters
        formatted = re.sub(r'(?<!^)(?=[A-Z])', ' ', entity_name)
        return formatted.strip()
    
    def get_entity_sets(self) -> List[str]:
        """Get all EntitySet names (available endpoints)"""
        entity_sets = []
        
        # Try different namespace patterns
        namespaces = [
            '{http://schemas.microsoft.com/ado/2008/09/edm}',
            '{http://schemas.microsoft.com/ado/2007/05/edm}',
            ''  # No namespace
        ]
        
        sets = []
        for ns in namespaces:
            sets = self.root.findall(f'.//{ns}EntitySet')
            if sets:
                break
        if not sets:
            sets = self.root.findall('.//EntitySet')
        
        for entity_set in sets:
            entity_set_name = entity_set.get('Name')
            if entity_set_name:
                entity_sets.append(entity_set_name)
        
        return sorted(entity_sets)
