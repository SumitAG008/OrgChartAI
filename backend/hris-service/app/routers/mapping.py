"""
HRIS Field Mapping API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, delete
from typing import List, Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.services.successfactors_client import SuccessFactorsClient
from app.services.metadata_parser import MetadataParser
import httpx
import base64

router = APIRouter(prefix="/connections", tags=["Field Mapping"])

# Pydantic models for mapping
class FieldMapping(BaseModel):
    entity_type: str  # 'org_unit', 'position', 'employee', 'fo_business_unit', etc.
    source_field: str  # SuccessFactors field name
    target_field: str  # OrgChartAI field name
    mapping_type: str = "direct"  # 'direct', 'transform', 'custom'
    transform_function: Optional[str] = None  # Optional transformation
    source_entity_name: Optional[str] = None  # SF entity name (e.g., 'FODepartment', 'FOBusinessUnit')

class FieldMappingResponse(FieldMapping):
    id: str
    connection_id: str

class MappingConfig(BaseModel):
    mappings: Dict[str, List[FieldMapping]]  # entity_type -> list of mappings

class SuccessFactorsEntity(BaseModel):
    name: str  # Entity name (e.g., "OrgUnit", "FOBusinessUnit")
    display_name: str  # User-friendly name
    description: Optional[str] = None
    fields_count: Optional[int] = None

class EntityField(BaseModel):
    name: str  # Field name (e.g., "orgUnitName")
    type: str  # Field type (e.g., "String", "DateTime", "NavigationProperty")
    nullable: bool = True
    description: Optional[str] = None

class EntityFieldsResponse(BaseModel):
    entity_name: str
    fields: List[EntityField]

class CredentialsRequest(BaseModel):
    company_id: str
    username: str
    password: str
    api_url: Optional[str] = "https://api.successfactors.eu"

@router.get("/{connection_id}/entities", response_model=List[SuccessFactorsEntity])
async def discover_entities(
    connection_id: str,
    fetch_from_sf: bool = False,  # Query parameter to force fetch from SF
    db: AsyncSession = Depends(get_db)
):
    """Discover all available SuccessFactors entities/APIs from $metadata"""
    # TODO: Get connection credentials from database
    # For now, if fetch_from_sf is True, fetch from actual SuccessFactors instance
    
    if fetch_from_sf:
        # Fetch $metadata from SuccessFactors
        # TODO: Get credentials from connection_id
        # For now, return error asking for credentials
        raise HTTPException(
            status_code=400,
            detail="Connection credentials not yet stored in database. Please provide credentials in request."
        )
    
    # Return empty list - user must fetch from SF to see real entities
    # This prevents showing incorrect/hardcoded entities
    return []

@router.post("/{connection_id}/fetch-metadata")
async def fetch_metadata_from_sf(
    connection_id: str,
    credentials: CredentialsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Fetch $metadata from SuccessFactors instance and parse all entities"""
    # TODO: Get credentials from database using connection_id
    # For now, accept credentials in request body
    
    company_id = credentials.company_id
    username = credentials.username
    password = credentials.password
    api_url = credentials.api_url or 'https://api.successfactors.eu'
    
    try:
        # Build Basic Auth header
        auth_string = f"{username}@{company_id}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        # Fetch $metadata
        metadata_url = f"{api_url}/odata/v2/$metadata"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metadata_url,
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Accept": "application/xml,application/json,*/*"
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch metadata: {response.text}"
                )
            
            # Parse metadata
            parser = MetadataParser(response.text)
            entities = parser.get_all_entities()
            entity_sets = parser.get_entity_sets()
            
            return {
                "success": True,
                "entities": entities,
                "entity_sets": entity_sets,
                "total_entities": len(entities),
                "metadata_url": metadata_url
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing metadata: {str(e)}")

@router.get("/{connection_id}/entities/{entity_name}/fields", response_model=EntityFieldsResponse)
async def get_entity_fields(
    connection_id: str,
    entity_name: str,
    fetch_from_sf: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Fetch all fields for a specific SuccessFactors entity from $metadata"""
    # Note: fetch_from_sf requires credentials, but we can't pass them in GET request body
    # Use POST endpoint instead for fetching from SF
    
    # Fallback: return mock fields
    entity_fields_map = {
        "OrgUnit": [
            {"name": "orgUnitId", "type": "String", "nullable": False},
            {"name": "orgUnitCode", "type": "String", "nullable": True},
            {"name": "orgUnitName", "type": "String", "nullable": False},
            {"name": "orgUnitType", "type": "String", "nullable": True},
            {"name": "parentOrgUnitId", "type": "String", "nullable": True},
            {"name": "status", "type": "String", "nullable": True},
        ],
    }
    
    fields = entity_fields_map.get(entity_name, [])
    return EntityFieldsResponse(
        entity_name=entity_name,
        fields=[EntityField(**field) for field in fields]
    )

@router.get("/{connection_id}/mapping/configs")
async def get_mapping_configs(
    connection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all mapping configurations grouped by target entity and source entity"""
    try:
        query = text("""
            SELECT 
                entity_type as target_entity_type,
                source_entity_name,
                COUNT(*) as field_count,
                MAX(updated_at) as last_updated
            FROM hris_field_mapping
            WHERE connection_id = :connection_id
            AND is_active = TRUE
            GROUP BY entity_type, source_entity_name
            ORDER BY entity_type, source_entity_name
        """)
        
        result = await db.execute(query, {"connection_id": connection_id})
        rows = result.fetchall()
        
        configs = []
        for row in rows:
            configs.append({
                "target_entity_type": row[0],
                "source_entity_name": row[1] or "Unknown",
                "field_count": row[2],
                "last_updated": row[3].isoformat() if row[3] else None
            })
        
        return configs
    
    except Exception as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            return []
        raise HTTPException(status_code=500, detail=f"Error fetching mapping configs: {str(e)}")

@router.get("/{connection_id}/mapping", response_model=MappingConfig)
async def get_mappings(
    connection_id: str,
    entity_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get field mappings for a connection, optionally filtered by entity type"""
    try:
        # Query from database - include source_entity_name
        query = text("""
            SELECT entity_type, source_entity_name, source_field, target_field, mapping_type, transform_function
            FROM hris_field_mapping
            WHERE connection_id = :connection_id
            AND is_active = TRUE
        """)
        
        params = {"connection_id": connection_id}
        if entity_type:
            query = text("""
                SELECT entity_type, source_entity_name, source_field, target_field, mapping_type, transform_function
                FROM hris_field_mapping
                WHERE connection_id = :connection_id
                AND entity_type = :entity_type
                AND is_active = TRUE
                ORDER BY source_entity_name, source_field
            """)
            params["entity_type"] = entity_type
        
        result = await db.execute(query, params)
        rows = result.fetchall()
        
        # Group by entity_type, then by source_entity_name
        all_mappings: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
        for row in rows:
            entity = row[0]
            source_entity = row[1] or "Unknown"
            
            if entity not in all_mappings:
                all_mappings[entity] = {}
            
            if source_entity not in all_mappings[entity]:
                all_mappings[entity][source_entity] = []
            
            all_mappings[entity][source_entity].append({
                "entity_type": entity,
                "source_entity_name": source_entity,
                "source_field": row[2],
                "target_field": row[3],
                "mapping_type": row[4],
                "transform_function": row[5]
            })
        
        # Flatten structure for backward compatibility
        # If entity_type filter, return flat list grouped by source entity
        if entity_type:
            return {"mappings": all_mappings.get(entity_type, {})}
        
        # Return nested structure: {entity_type: {source_entity: [mappings]}}
        return {"mappings": all_mappings}
        
        if entity_type:
            return {"mappings": {entity_type: all_mappings.get(entity_type, [])}}
        
        return {"mappings": all_mappings}
        
    except Exception as e:
        # If table doesn't exist, return empty mappings
        if "does not exist" in str(e) or "relation" in str(e).lower():
            return {"mappings": {}}
        raise HTTPException(status_code=500, detail=f"Error fetching mappings: {str(e)}")

@router.post("/{connection_id}/mapping", response_model=Dict[str, Any])
async def save_mappings(
    connection_id: str,
    config: MappingConfig,
    db: AsyncSession = Depends(get_db)
):
    """Save field mappings for a connection to database"""
    try:
        # Start a transaction - db.begin() keeps connection open and auto-commits
        async with db.begin():
            # First, deactivate existing mappings for this connection
            deactivate_query = text("""
                UPDATE hris_field_mapping
                SET is_active = FALSE, updated_at = :updated_at
                WHERE connection_id = :connection_id
            """)
            await db.execute(
                deactivate_query,
                {"connection_id": connection_id, "updated_at": datetime.utcnow()}
            )
            await db.flush()  # Ensure query executes before continuing
            
            # Insert new mappings
            saved_count = 0
            source_entity_name = None  # Will be extracted from mappings or request
            
            for entity_type, mappings in config.mappings.items():
                if not mappings:
                    continue
                
                # Get source_entity_name from first mapping (all mappings in a batch should have same source entity)
                source_entity_name = getattr(mappings[0], 'source_entity_name', None)
                
                # Deactivate existing mappings for this specific source entity and target
                if source_entity_name:
                    deactivate_specific = text("""
                        UPDATE hris_field_mapping
                        SET is_active = FALSE, updated_at = :updated_at
                        WHERE connection_id = :connection_id
                        AND entity_type = :entity_type
                        AND source_entity_name = :source_entity_name
                    """)
                    await db.execute(
                        deactivate_specific,
                        {
                            "connection_id": connection_id,
                            "entity_type": entity_type,
                            "source_entity_name": source_entity_name,
                            "updated_at": datetime.utcnow()
                        }
                    )
                
                for mapping in mappings:
                    # Use mapping's source_entity_name or fallback
                    mapping_source_entity = getattr(mapping, 'source_entity_name', None) or source_entity_name
                    
                    insert_query = text("""
                        INSERT INTO hris_field_mapping 
                        (connection_id, entity_type, source_entity_name, source_field, target_field, mapping_type, transform_function, is_active, created_at, updated_at)
                        VALUES (:connection_id, :entity_type, :source_entity_name, :source_field, :target_field, :mapping_type, :transform_function, TRUE, :created_at, :updated_at)
                        ON CONFLICT (connection_id, entity_type, source_entity_name, source_field)
                        DO UPDATE SET
                            target_field = EXCLUDED.target_field,
                            mapping_type = EXCLUDED.mapping_type,
                            transform_function = EXCLUDED.transform_function,
                            is_active = TRUE,
                            updated_at = EXCLUDED.updated_at
                    """)
                    await db.execute(
                        insert_query,
                        {
                            "connection_id": connection_id,
                            "entity_type": entity_type,
                            "source_entity_name": mapping_source_entity,
                            "source_field": mapping.source_field,
                            "target_field": mapping.target_field,
                            "mapping_type": mapping.mapping_type,
                            "transform_function": mapping.transform_function,
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    )
                    await db.flush()  # Ensure each insert executes
                    saved_count += 1
                
                # Update or insert mapping config
                if source_entity_name:
                    config_query = text("""
                        INSERT INTO hris_mapping_config 
                        (connection_id, target_entity_type, source_entity_name, hris_source, is_active, created_at, updated_at)
                        VALUES (:connection_id, :target_entity_type, :source_entity_name, :hris_source, TRUE, :created_at, :updated_at)
                        ON CONFLICT (connection_id, target_entity_type, source_entity_name)
                        DO UPDATE SET
                            is_active = TRUE,
                            updated_at = EXCLUDED.updated_at
                    """)
                    await db.execute(
                        config_query,
                        {
                            "connection_id": connection_id,
                            "target_entity_type": entity_type,
                            "source_entity_name": source_entity_name,
                            "hris_source": "successfactors",
                            "created_at": datetime.utcnow(),
                            "updated_at": datetime.utcnow()
                        }
                    )
                    await db.flush()  # Ensure config update executes
            
            # Transaction auto-commits when exiting 'async with db.begin()' block
        
        return {
            "success": True,
            "message": f"Successfully saved {saved_count} field mappings to database",
            "connection_id": connection_id,
            "mappings_saved": saved_count,
            "entity_types": list(config.mappings.keys()),
            "storage_location": "PostgreSQL database (hris_field_mapping table)"
        }
        
    except Exception as e:
        # If table doesn't exist, provide helpful error
        if "does not exist" in str(e) or "relation" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail=f"Database table 'hris_field_mapping' does not exist. Please run: python backend/hris-service/setup_mapping_tables.py"
            )
        raise HTTPException(status_code=500, detail=f"Error saving mappings: {str(e)}")

@router.get("/{connection_id}/mapping/verify", response_model=Dict[str, Any])
async def verify_mappings(
    connection_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Verify saved mappings exist in database"""
    try:
        # Count total mappings
        count_query = text("""
            SELECT 
                COUNT(*) as total,
                COUNT(DISTINCT entity_type) as entity_types_count,
                COUNT(CASE WHEN transform_function IS NOT NULL THEN 1 END) as with_transforms
            FROM hris_field_mapping
            WHERE connection_id = :connection_id
            AND is_active = TRUE
        """)
        
        result = await db.execute(count_query, {"connection_id": connection_id})
        row = result.fetchone()
        
        total = row[0] if row else 0
        entity_types_count = row[1] if row else 0
        with_transforms = row[2] if row else 0
        
        # Get mappings by entity type
        detail_query = text("""
            SELECT 
                entity_type,
                COUNT(*) as count
            FROM hris_field_mapping
            WHERE connection_id = :connection_id
            AND is_active = TRUE
            GROUP BY entity_type
            ORDER BY entity_type
        """)
        
        detail_result = await db.execute(detail_query, {"connection_id": connection_id})
        details = {row[0]: row[1] for row in detail_result.fetchall()}
        
        # Check if mapping config exists
        config_query = text("""
            SELECT target_entity_type, source_entity_name, last_synced_at
            FROM hris_mapping_config
            WHERE connection_id = :connection_id
            AND is_active = TRUE
        """)
        
        config_result = await db.execute(config_query, {"connection_id": connection_id})
        configs = [
            {
                "target_entity_type": row[0],
                "source_entity_name": row[1],
                "last_synced_at": row[2].isoformat() if row[2] else None
            }
            for row in config_result.fetchall()
        ]
        
        return {
            "connection_id": connection_id,
            "verified": True,
            "total_mappings": total,
            "entity_types": entity_types_count,
            "mappings_with_transforms": with_transforms,
            "details_by_entity": details,
            "configurations": configs,
            "database": "PostgreSQL (hris_field_mapping table)",
            "status": "active" if total > 0 else "no_mappings"
        }
        
    except Exception as e:
        if "does not exist" in str(e) or "relation" in str(e).lower():
            return {
                "connection_id": connection_id,
                "verified": False,
                "error": "Database tables do not exist",
                "message": "Please run setup_mapping_tables.py to create the tables"
            }
        raise HTTPException(status_code=500, detail=f"Error verifying mappings: {str(e)}")

@router.post("/{connection_id}/entities/{entity_name}/fetch-fields")
async def fetch_fields_from_sf(
    connection_id: str,
    entity_name: str,
    credentials: CredentialsRequest,
    db: AsyncSession = Depends(get_db)
):
    """Fetch fields directly from SuccessFactors instance using connection credentials"""
    # TODO: Get credentials from database using connection_id
    # For now, accept credentials in request body
    
    company_id = credentials.company_id
    username = credentials.username
    password = credentials.password
    api_url = credentials.api_url or 'https://api.successfactors.eu'
    
    try:
        # Build Basic Auth header
        auth_string = f"{username}@{company_id}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        
        # Fetch $metadata
        metadata_url = f"{api_url}/odata/v2/$metadata"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                metadata_url,
                headers={
                    "Authorization": f"Basic {encoded_auth}",
                    "Accept": "application/xml,application/json,*/*"
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch metadata: {response.text}"
                )
            
            # Parse metadata and get fields for this entity
            parser = MetadataParser(response.text)
            fields = parser.get_entity_fields(entity_name)
            
            return {
                "success": True,
                "entity_name": entity_name,
                "fields": fields,
                "fields_count": len(fields),
                "message": f"Successfully fetched {len(fields)} fields for {entity_name}"
            }
    
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching fields: {str(e)}")