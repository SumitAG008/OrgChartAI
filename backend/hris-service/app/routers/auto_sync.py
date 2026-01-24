"""
Auto Sync - One-Click SuccessFactors Sync
Automatically discovers entities, creates default mappings, and syncs all data
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.services.successfactors_client import SuccessFactorsClient
from app.services.metadata_parser import MetadataParser
from app.services.sync_service import SyncService
# Encryption not needed for auto sync - credentials passed directly
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import httpx
import base64
import logging
import json

logger = logging.getLogger(__name__)

def serialize_for_json(obj: Any) -> Any:
    """Convert datetime and other non-JSON-serializable objects to JSON-compatible types"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    return obj

async def send_to_org_service(entity_type: str, data: List[Dict[str, Any]]) -> bool:
    """Send transformed data to org-service"""
    try:
        org_service_url = "http://localhost:8000/api/v1"

        # Map entity types to org-service endpoints
        endpoint_map = {
            "org_unit": f"{org_service_url}/org-units/bulk",
            "position": f"{org_service_url}/positions/bulk",
            "employee": f"{org_service_url}/employees/bulk"
        }

        endpoint = endpoint_map.get(entity_type)
        if not endpoint:
            logger.warning(f"No endpoint for entity type: {entity_type}")
            return False

        # Serialize data to ensure all datetime objects are converted
        serialized_data = serialize_for_json(data)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json={"records": serialized_data})
            response.raise_for_status()
            return True
    except Exception as e:
        logger.error(f"Error sending data to org-service: {str(e)}")
        return False

router = APIRouter()

# In-memory sync status storage
auto_sync_store: Dict[str, Dict[str, Any]] = {}

# Default field mappings for common SuccessFactors entities
DEFAULT_MAPPINGS = {
    "FOLegalEntity": {
        "target_entity": "org_unit",
        "mappings": [
            {"source": "externalCode", "target": "hris_id", "transform": None},
            {"source": "name", "target": "name", "transform": None},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id", "transform": None},
            {"source": "externalCode", "target": "code", "transform": None},
        ]
    },
    "FODepartment": {
        "target_entity": "org_unit",
        "mappings": [
            {"source": "externalCode", "target": "hris_id", "transform": None},
            {"source": "name", "target": "name", "transform": None},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id", "transform": None},
            {"source": "externalCode", "target": "code", "transform": None},
        ]
    },
    "FODivision": {
        "target_entity": "org_unit",
        "mappings": [
            {"source": "externalCode", "target": "hris_id", "transform": None},
            {"source": "name", "target": "name", "transform": None},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id", "transform": None},
            {"source": "externalCode", "target": "code", "transform": None},
        ]
    },
    "FOBusinessUnit": {
        "target_entity": "org_unit",
        "mappings": [
            {"source": "externalCode", "target": "hris_id", "transform": None},
            {"source": "name", "target": "name", "transform": None},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id", "transform": None},
            {"source": "externalCode", "target": "code", "transform": None},
        ]
    },
    "FOCostCenter": {
        "target_entity": "org_unit",
        "mappings": [
            {"source": "externalCode", "target": "hris_id", "transform": None},
            {"source": "name", "target": "name", "transform": None},
            {"source": "status", "target": "status", "transform": "status_active"},
            {"source": "parent", "target": "parent_id", "transform": None},
            {"source": "externalCode", "target": "code", "transform": None},
        ]
    },
    "Position": {
        "target_entity": "position",
        "mappings": [
            {"source": "positionId", "target": "hris_id", "transform": None},
            {"source": "positionTitle", "target": "title", "transform": None},
            {"source": "positionCode", "target": "code", "transform": None},
            {"source": "code", "target": "code", "transform": None},  # Fallback for code field
            {"source": "orgUnit", "target": "org_unit_id", "transform": None},
            {"source": "jobCode", "target": "job_code", "transform": None},
        ]
    },
    "PerPerson": {
        "target_entity": "employee",
        "mappings": [
            {"source": "personIdExternal", "target": "hris_id", "transform": None},
            {"source": "personId", "target": "hris_id", "transform": None},  # Fallback ID field
            {"source": "firstName", "target": "first_name", "transform": None},
            {"source": "lastName", "target": "last_name", "transform": None},
            {"source": "emailAddress", "target": "email", "transform": "lowercase"},  # Standard SF field name
        ]
    },
    "User": {
        "target_entity": "employee",
        "mappings": [
            {"source": "userId", "target": "hris_id", "transform": None},
            {"source": "firstName", "target": "first_name", "transform": None},
            {"source": "lastName", "target": "last_name", "transform": None},
            {"source": "email", "target": "email", "transform": "lowercase"},
            {"source": "status", "target": "status", "transform": "status_active"},
        ]
    }
}

async def create_default_mappings(
    db: AsyncSession,
    connection_id: str,
    entity_name: str,
    target_entity: str,
    mappings: List[Dict[str, Any]]
):
    """Create default field mappings for an entity"""
    try:
        # Check if mapping config exists
        check_config = text("""
            SELECT id FROM hris_mapping_config
            WHERE connection_id = :connection_id
            AND target_entity_type = :target_entity
            AND source_entity_name = :source_entity
        """)
        result = await db.execute(check_config, {
            "connection_id": connection_id,
            "target_entity": target_entity,
            "source_entity": entity_name
        })
        config_exists = result.fetchone()
        
        if not config_exists:
            # Create mapping config
            config_id = str(uuid.uuid4())
            insert_config = text("""
                INSERT INTO hris_mapping_config 
                (id, connection_id, target_entity_type, source_entity_name, is_active, created_at, updated_at)
                VALUES (:id, :connection_id, :target_entity, :source_entity, TRUE, :now, :now)
            """)
            await db.execute(insert_config, {
                "id": config_id,
                "connection_id": connection_id,
                "target_entity": target_entity,
                "source_entity": entity_name,
                "now": datetime.utcnow()
            })
        
        # Create field mappings
        for mapping in mappings:
            check_mapping = text("""
                SELECT id FROM hris_field_mapping
                WHERE connection_id = :connection_id
                AND entity_type = :target_entity
                AND source_entity_name = :source_entity
                AND source_field = :source_field
                AND target_field = :target_field
            """)
            result = await db.execute(check_mapping, {
                "connection_id": connection_id,
                "target_entity": target_entity,
                "source_entity": entity_name,
                "source_field": mapping["source"],
                "target_field": mapping["target"]
            })
            mapping_exists = result.fetchone()
            
            if not mapping_exists:
                mapping_id = str(uuid.uuid4())
                insert_mapping = text("""
                    INSERT INTO hris_field_mapping
                    (id, connection_id, entity_type, source_entity_name, source_field, 
                     target_field, transform_function, is_active, created_at, updated_at)
                    VALUES (:id, :connection_id, :target_entity, :source_entity, :source_field,
                            :target_field, :transform, TRUE, :now, :now)
                """)
                await db.execute(insert_mapping, {
                    "id": mapping_id,
                    "connection_id": connection_id,
                    "target_entity": target_entity,
                    "source_entity": entity_name,
                    "source_field": mapping["source"],
                    "target_field": mapping["target"],
                    "transform": mapping.get("transform"),
                    "now": datetime.utcnow()
                })
        
        await db.commit()
        logger.info(f"Created default mappings for {entity_name} -> {target_entity}")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating mappings for {entity_name}: {str(e)}")
        raise

async def auto_sync_task(
    sync_id: str,
    connection_id: str,
    company_id: str,
    username: str,
    password: str,
    api_url: str
):
    """Background task for auto sync"""
    logger.info(f"=== AUTO SYNC TASK STARTED ===")
    logger.info(f"Sync ID: {sync_id}")
    logger.info(f"Connection ID: {connection_id}")
    logger.info(f"Company ID: {company_id}")
    logger.info(f"Username: {username}")
    logger.info(f"API URL: {api_url}")

    try:
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            # Update status
            auto_sync_store[sync_id].update({
                "status": "discovering",
                "message": "Discovering SuccessFactors entities..."
            })
            
            # Step 1: Discover entities from SuccessFactors
            # Use SuccessFactorsClient for proper authentication
            client = SuccessFactorsClient(
                company_id=company_id,
                username=username,
                password=password,
                api_url=api_url
            )
            
            # Authenticate first
            logger.info(f"Authenticating with SuccessFactors...")
            if not await client.authenticate():
                logger.error("Authentication failed!")
                raise Exception("Failed to authenticate with SuccessFactors. Please check your credentials.")
            logger.info("Authentication successful!")
            
            # Fetch metadata using authenticated client
            metadata_url = f"{api_url}/odata/v2/$metadata"
            async with httpx.AsyncClient() as http_client:
                # Use Basic Auth header from client
                headers = {
                    "Authorization": client.basic_auth_header or f"Bearer {client.access_token}",
                    "Accept": "application/xml,application/json,*/*"
                }
                response = await http_client.get(
                    metadata_url,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 401:
                    raise Exception(f"Authentication failed (401). Please verify your credentials. API URL: {api_url}")
                
                response.raise_for_status()
                metadata_xml = response.text
            
            # Parse metadata
            logger.info(f"Parsing metadata ({len(metadata_xml)} bytes)...")
            parser = MetadataParser(metadata_xml)
            all_entities = parser.get_all_entities()
            logger.info(f"Found {len(all_entities)} total entities in metadata")

            # Filter for org structure entities - IN SPECIFIC SEQUENCE
            # Order matters: Org Units first, then Positions, then Employees
            org_structure_entities_ordered = [
                # Phase 1: Org Units (must sync first to establish hierarchy)
                "FODepartment",
                "FOCostCenter", 
                "FOLegalEntity",
                "FODivision",
                "FOBusinessUnit",
                # Phase 2: Positions (depend on org units)
                "Position",
                # Phase 3: Employees (depend on positions)
                "PerPerson",
                "User"
            ]
            
            # Find entities that exist in SF, maintaining order
            found_entities = [e for e in org_structure_entities_ordered if e in all_entities]
            logger.info(f"Found {len(found_entities)} org structure entities: {found_entities}")

            auto_sync_store[sync_id].update({
                "status": "mapping",
                "message": f"Found {len(found_entities)} entities. Creating mappings...",
                "entities_found": found_entities
            })
            
            # Step 2: Create default mappings for found entities
            for entity_name in found_entities:
                if entity_name in DEFAULT_MAPPINGS:
                    mapping_config = DEFAULT_MAPPINGS[entity_name]
                    await create_default_mappings(
                        db,
                        connection_id,
                        entity_name,
                        mapping_config["target_entity"],
                        mapping_config["mappings"]
                    )
            
            auto_sync_store[sync_id].update({
                "status": "syncing",
                "message": "Starting data sync..."
            })
            
            # Step 3: Run comprehensive sync IN SEQUENCE
            sync_service = SyncService(db)
            
            # Group entities by phase for better logging
            org_unit_entities = ["FODepartment", "FOCostCenter", "FOLegalEntity", "FODivision", "FOBusinessUnit"]
            position_entities = ["Position"]
            employee_entities = ["PerPerson", "User"]
            
            # Sync all entities in order: Org Units → Positions → Employees
            all_results = []
            total_records = 0
            processed_records = 0
            failed_records = 0
            errors = []
            
            logger.info(f"Starting sequential sync: {len(found_entities)} entities found")
            logger.info(f"Phase 1 - Org Units: {[e for e in found_entities if e in org_unit_entities]}")
            logger.info(f"Phase 2 - Positions: {[e for e in found_entities if e in position_entities]}")
            logger.info(f"Phase 3 - Employees: {[e for e in found_entities if e in employee_entities]}")
            
            # Sync in sequence
            for entity_name in found_entities:
                if entity_name in DEFAULT_MAPPINGS:
                    mapping_config = DEFAULT_MAPPINGS[entity_name]
                    target_entity = mapping_config["target_entity"]
                    
                    try:
                        # Update status with current entity being synced
                        phase = "Org Units" if entity_name in org_unit_entities else ("Positions" if entity_name in position_entities else "Employees")
                        auto_sync_store[sync_id].update({
                            "status": "syncing",
                            "message": f"Syncing {phase}: {entity_name}...",
                            "current_entity": entity_name
                        })
                        
                        logger.info(f"Syncing {entity_name} -> {target_entity}...")
                        
                        result = await sync_service.sync_entity(
                            connection_id,
                            target_entity,
                            entity_name,
                            None  # No limit
                        )
                        
                        all_results.append(result)
                        
                        if result["success"]:
                            total_records += result["records_fetched"]
                            logger.info(f"✓ {entity_name}: Fetched {result['records_fetched']} records")
                            
                            # Send to org-service
                            if await send_to_org_service(target_entity, result["data"]):
                                processed_records += result["records_fetched"]
                                logger.info(f"✓ {entity_name}: Sent {result['records_fetched']} records to org-service")
                            else:
                                failed_records += result["records_fetched"]
                                errors.append(f"Failed to send {entity_name} to org-service")
                                logger.warning(f"✗ {entity_name}: Failed to send to org-service")
                        else:
                            failed_records += result.get("records_fetched", 0)
                            error_msg = result.get('error', 'Unknown error')
                            errors.append(f"{entity_name}: {error_msg}")
                            logger.error(f"✗ {entity_name}: {error_msg}")
                            
                    except Exception as e:
                        logger.error(f"Error syncing {entity_name}: {str(e)}")
                        errors.append(f"{entity_name}: {str(e)}")
            
            # Update final status
            auto_sync_store[sync_id].update({
                "status": "completed" if failed_records == 0 else "failed",
                "message": f"Sync completed. Processed {processed_records} records.",
                "total_records": total_records,
                "processed_records": processed_records,
                "failed_records": failed_records,
                "errors": errors,
                "results": all_results,
                "completed_at": datetime.utcnow()
            })
            
            # Update connection
            update_query = text("""
                UPDATE hris_connection
                SET last_sync_at = :sync_time,
                    last_sync_status = :sync_status
                WHERE id = :connection_id
            """)
            await db.execute(update_query, {
                "sync_time": datetime.utcnow(),
                "sync_status": "completed" if failed_records == 0 else "failed",
                "connection_id": connection_id
            })
            await db.commit()
            
    except Exception as e:
        logger.error(f"Auto sync task error: {str(e)}")
        auto_sync_store[sync_id].update({
            "status": "failed",
            "message": f"Error: {str(e)}",
            "errors": [str(e)],
            "completed_at": datetime.utcnow()
        })

from pydantic import BaseModel

class AutoSyncCredentials(BaseModel):
    company_id: str
    username: str
    password: str
    api_url: str = "https://api.successfactors.eu"

@router.post("/auto-sync/start")
async def start_auto_sync(
    connection_id: str,
    credentials: AutoSyncCredentials,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    One-Click Auto Sync - Just provide connection credentials
    
    This endpoint:
    1. Discovers all SuccessFactors entities automatically
    2. Creates default field mappings
    3. Syncs all org structure data
    
    No manual mapping configuration required!
    """
    sync_id = str(uuid.uuid4())
    
    # Try to get connection name, or create connection if it doesn't exist
    connection_name = "Auto Sync Connection"
    try:
        check_connection = text("""
            SELECT id, name FROM hris_connection
            WHERE id = :connection_id
        """)
        result = await db.execute(check_connection, {"connection_id": connection_id})
        connection = result.fetchone()
        
        if connection:
            connection_name = connection[1]
        else:
            # Create connection if it doesn't exist
            # Use JSONB cast in SQL instead of passing JSON string
            from sqlalchemy.dialects.postgresql import JSONB
            
            credentials_dict = {
                "company_id": credentials.company_id,
                "username": credentials.username,
                "api_url": credentials.api_url,
                "auth_method": "basic"
            }
            
            create_connection = text("""
                INSERT INTO hris_connection (id, name, system, status, credentials, is_active, created_at, updated_at)
                VALUES (:id, :name, 'successfactors', 'active', CAST(:credentials AS jsonb), TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """)
            await db.execute(create_connection, {
                "id": connection_id,
                "name": connection_name,
                "credentials": json.dumps(credentials_dict)  # Pass as JSON string, cast to JSONB in SQL
            })
            await db.commit()
            logger.info(f"Created connection {connection_id} for auto sync")
    except Exception as e:
        logger.warning(f"Could not check/create connection: {e}")
        # Continue anyway - we'll use the connection_id
        await db.rollback()
    
    # Initialize sync status
    auto_sync_store[sync_id] = {
        "sync_id": sync_id,
        "status": "pending",
        "message": "Initializing auto sync...",
        "connection_id": connection_id,
        "connection_name": connection_name,
        "started_at": datetime.utcnow(),
        "total_records": 0,
        "processed_records": 0,
        "failed_records": 0,
        "errors": []
    }
    
    # Start background task
    background_tasks.add_task(
        auto_sync_task,
        sync_id,
        connection_id,
        credentials.company_id,
        credentials.username,
        credentials.password,
        credentials.api_url
    )
    
    return {
        "sync_id": sync_id,
        "status": "pending",
        "message": "Auto sync started. Discovering entities and creating mappings...",
        "connection_id": connection_id,
        "connection_name": connection_name,
        "started_at": datetime.utcnow().isoformat()
    }

@router.get("/auto-sync/{sync_id}")
async def get_auto_sync_status(
    sync_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get auto sync status"""
    if sync_id not in auto_sync_store:
        raise HTTPException(status_code=404, detail="Sync job not found")
    
    return auto_sync_store[sync_id]

@router.get("/auto-sync/")
async def list_auto_syncs(
    connection_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all auto sync jobs"""
    results = []
    for sync_id, status_data in list(auto_sync_store.items())[-limit:]:
        if connection_id and status_data.get("connection_id") != connection_id:
            continue
        
        results.append({
            "sync_id": status_data["sync_id"],
            "status": status_data["status"],
            "message": status_data.get("message", ""),
            "connection_id": status_data["connection_id"],
            "connection_name": status_data.get("connection_name", ""),
            "started_at": status_data["started_at"],
            "total_records": status_data.get("total_records", 0),
            "processed_records": status_data.get("processed_records", 0),
            "failed_records": status_data.get("failed_records", 0),
            "completed_at": status_data.get("completed_at")
        })
    
    return results
