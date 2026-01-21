"""
Sync Service - Handles data synchronization from HRIS to OrgChartAI
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.services.successfactors_client import SuccessFactorsClient
from app.services.data_transformer import DataTransformer
from app.services.transform_functions import TransformFunctions
from app.services.metadata_parser import MetadataParser
from datetime import datetime
import httpx
import logging

logger = logging.getLogger(__name__)

class SyncService:
    """Service for syncing data from HRIS systems"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.transformer = DataTransformer(db)
        self.transform_functions = TransformFunctions()
    
    async def get_connection_credentials(self, connection_id: str) -> Dict[str, Any]:
        """Get connection credentials from database"""
        query = text("""
            SELECT credentials, system, name
            FROM hris_connection
            WHERE id = :connection_id AND is_active = TRUE
        """)
        result = await self.db.execute(query, {"connection_id": connection_id})
        row = result.fetchone()
        
        if not row:
            raise ValueError(f"Connection {connection_id} not found or inactive")
        
        # Decrypt credentials if needed (for now, assume plain text)
        credentials = row[0] if isinstance(row[0], dict) else {}
        return {
            "company_id": credentials.get("company_id"),
            "username": credentials.get("username"),
            "password": credentials.get("password"),
            "api_url": credentials.get("api_url", "https://api.successfactors.eu"),
            "system": row[1],
            "name": row[2]
        }
    
    async def get_mappings_for_entity(
        self, 
        connection_id: str, 
        entity_type: str, 
        source_entity_name: str
    ) -> List[Dict[str, Any]]:
        """Get field mappings for a specific entity"""
        query = text("""
            SELECT source_field, target_field, mapping_type, transform_function
            FROM hris_field_mapping
            WHERE connection_id = :connection_id
            AND entity_type = :entity_type
            AND source_entity_name = :source_entity_name
            AND is_active = TRUE
        """)
        result = await self.db.execute(
            query,
            {
                "connection_id": connection_id,
                "entity_type": entity_type,
                "source_entity_name": source_entity_name
            }
        )
        rows = result.fetchall()
        
        return [
            {
                "source_field": row[0],
                "target_field": row[1],
                "mapping_type": row[2],
                "transform_function": row[3]
            }
            for row in rows
        ]
    
    async def get_mapping_configs(self, connection_id: str) -> List[Dict[str, Any]]:
        """Get all mapping configurations for a connection"""
        query = text("""
            SELECT target_entity_type, source_entity_name
            FROM hris_mapping_config
            WHERE connection_id = :connection_id
            AND is_active = TRUE
        """)
        result = await self.db.execute(query, {"connection_id": connection_id})
        rows = result.fetchall()
        
        return [
            {
                "target_entity_type": row[0],
                "source_entity_name": row[1]
            }
            for row in rows
        ]
    
    async def fetch_and_transform_data(
        self,
        connection_id: str,
        entity_type: str,
        source_entity_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Fetch data from SuccessFactors and transform using mappings"""
        # Get connection credentials
        creds = await self.get_connection_credentials(connection_id)
        
        # Get mappings for this entity
        mappings = await self.get_mappings_for_entity(
            connection_id, 
            entity_type, 
            source_entity_name
        )
        
        if not mappings:
            logger.warning(f"No mappings found for {entity_type} from {source_entity_name}")
            return []
        
        # Create SuccessFactors client
        client = SuccessFactorsClient(
            company_id=creds["company_id"],
            username=creds["username"],
            password=creds["password"],
            api_url=creds["api_url"]
        )
        
        # Authenticate
        if not await client.authenticate():
            raise Exception("Failed to authenticate with SuccessFactors")
        
        # Fetch data from SF based on entity type
        sf_data = []
        try:
            if source_entity_name in ["FOLegalEntity", "FODepartment", "FODivision", "FOBusinessUnit", "FOCostCenter"]:
                # Org Unit entities
                if source_entity_name == "FOLegalEntity":
                    sf_data = await client.get_legal_entities(top=limit)
                elif source_entity_name == "FODepartment":
                    sf_data = await client.get_departments(top=limit)
                elif source_entity_name == "FODivision":
                    sf_data = await client.get_divisions(top=limit)
                elif source_entity_name == "FOBusinessUnit":
                    sf_data = await client.get_business_units(top=limit)
                elif source_entity_name == "FOCostCenter":
                    sf_data = await client.get_cost_centers(top=limit)
                else:
                    sf_data = await client.get_org_units(source_entity_name, top=limit)
            elif source_entity_name == "Position":
                positions = await client.get_positions(top=limit)
                sf_data = [dict(pos) if hasattr(pos, '__dict__') else pos for pos in positions]
            elif source_entity_name in ["PerPerson", "User"]:
                if source_entity_name == "PerPerson":
                    sf_data = await client.get_per_person(top=limit)
                else:
                    users = await client.get_users(top=limit)
                    sf_data = [dict(user) if hasattr(user, '__dict__') else user for user in users]
            else:
                # Custom MDF object or unknown entity - try generic fetch
                sf_data = await client.get_custom_mdf_object(source_entity_name, top=limit)
            
            # sf_data is already a list of dicts from the client methods
            # No need to extract from OData format
            results = sf_data if isinstance(sf_data, list) else []
            
            logger.info(f"Fetched {len(results)} records from {source_entity_name}")
            
            # Transform data using mappings
            transformed_data = []
            for record in results:
                transformed = await self._apply_mappings(
                    record, 
                    mappings, 
                    entity_type,
                    source_entity_name
                )
                if transformed:
                    transformed_data.append(transformed)
            
            return transformed_data
            
        except Exception as e:
            logger.error(f"Error fetching data from {source_entity_name}: {str(e)}")
            raise
    
    async def _apply_mappings(
        self,
        source_record: Dict[str, Any],
        mappings: List[Dict[str, Any]],
        entity_type: str,
        source_entity_name: str
    ) -> Optional[Dict[str, Any]]:
        """Apply field mappings and transformations to a source record"""
        transformed = {
            "hris_id": None,
            "hris_source": "successfactors",
            "hris_type": source_entity_name
        }
        
        # Apply each mapping
        for mapping in mappings:
            source_field = mapping["source_field"]
            target_field = mapping["target_field"]
            transform_func = mapping.get("transform_function")
            
            # Get source value
            source_value = source_record.get(source_field)
            
            # Apply transformation if specified
            if transform_func:
                try:
                    transformed_value = self._apply_transform(
                        source_value, 
                        transform_func,
                        source_record,
                        source_entity_name
                    )
                except Exception as e:
                    logger.warning(f"Transform error for {source_field}: {str(e)}")
                    transformed_value = source_value
            else:
                transformed_value = source_value
            
            # Set target field
            transformed[target_field] = transformed_value
            
            # Store hris_id if mapped
            if target_field == "hris_id" or source_field.endswith("Id") or source_field.endswith("Code"):
                if not transformed.get("hris_id") and transformed_value:
                    transformed["hris_id"] = str(transformed_value)
        
        # Ensure hris_id is set (use first available ID field)
        if not transformed.get("hris_id"):
            for key in ["externalCode", "code", "id", "userId", "positionId", "orgUnitId"]:
                if key in source_record and source_record[key]:
                    transformed["hris_id"] = str(source_record[key])
                    break
        
        return transformed
    
    def _apply_transform(
        self,
        value: Any,
        transform_func: str,
        source_record: Dict[str, Any],
        source_entity_name: str
    ) -> Any:
        """Apply a transformation function to a value"""
        if not transform_func:
            return value
        
        # Handle constant transformation
        if transform_func.startswith("constant("):
            # Extract constant value: constant('value')
            constant_value = transform_func.replace("constant(", "").replace(")", "").strip("'\"")
            return constant_value
        
        # Handle map_org_unit_type
        if transform_func == "map_org_unit_type":
            return self.transform_functions.map_org_unit_type(value, source_entity_name)
        
        # Handle other transformations
        if transform_func == "uppercase":
            return self.transform_functions.transform_uppercase(value)
        elif transform_func == "lowercase":
            return self.transform_functions.transform_lowercase(value)
        elif transform_func == "title_case":
            return self.transform_functions.transform_title_case(value)
        elif transform_func == "trim":
            return self.transform_functions.transform_trim(value)
        elif transform_func == "status_active":
            return self.transform_functions.transform_status_active(value)
        elif transform_func == "boolean":
            return self.transform_functions.transform_boolean(value)
        elif transform_func.startswith("date_format"):
            # Extract format: date_format('ISO','YYYY-MM-DD')
            parts = transform_func.replace("date_format(", "").replace(")", "").split(",")
            if len(parts) >= 2:
                return self.transform_functions.transform_date_format(
                    value, 
                    parts[0].strip("'\""), 
                    parts[1].strip("'\"")
                )
        elif transform_func.startswith("round"):
            # Extract decimal places: round(2)
            decimal_places = int(transform_func.replace("round(", "").replace(")", ""))
            return self.transform_functions.transform_round(value, decimal_places)
        
        return value
    
    async def sync_entity(
        self,
        connection_id: str,
        entity_type: str,
        source_entity_name: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sync a specific entity type"""
        try:
            # Fetch and transform data
            transformed_data = await self.fetch_and_transform_data(
                connection_id,
                entity_type,
                source_entity_name,
                limit
            )
            
            # Send to org-service
            # For now, return the data (org-service endpoint will be called separately)
            return {
                "success": True,
                "entity_type": entity_type,
                "source_entity_name": source_entity_name,
                "records_fetched": len(transformed_data),
                "data": transformed_data
            }
        except Exception as e:
            logger.error(f"Error syncing {entity_type} from {source_entity_name}: {str(e)}")
            return {
                "success": False,
                "entity_type": entity_type,
                "source_entity_name": source_entity_name,
                "error": str(e),
                "records_fetched": 0,
                "data": []
            }
    
    async def sync_all_entities(
        self,
        connection_id: str,
        entity_types: Optional[List[str]] = None,
        limit_per_entity: Optional[int] = None
    ) -> Dict[str, Any]:
        """Sync all configured entities"""
        # Get all mapping configs
        configs = await self.get_mapping_configs(connection_id)
        
        if not configs:
            return {
                "success": False,
                "message": "No mappings configured for this connection",
                "results": []
            }
        
        results = []
        total_records = 0
        
        for config in configs:
            target_entity = config["target_entity_type"]
            source_entity = config["source_entity_name"]
            
            # Filter by entity_types if specified
            if entity_types and target_entity not in entity_types:
                continue
            
            # Sync this entity
            result = await self.sync_entity(
                connection_id,
                target_entity,
                source_entity,
                limit_per_entity
            )
            
            results.append(result)
            if result["success"]:
                total_records += result["records_fetched"]
        
        return {
            "success": True,
            "total_records": total_records,
            "results": results
        }
