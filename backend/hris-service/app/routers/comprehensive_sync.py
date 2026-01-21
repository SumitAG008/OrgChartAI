"""
Comprehensive SuccessFactors Sync Endpoint
Syncs all org structure entities: FOLegalEntity, FODepartment, FODivision, 
FOBusinessUnit, FOCostCenter, Position, PerPerson, User, and Custom MDF objects
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.sync_service import SyncService
from app.models import SyncRequest, SyncResponse, SyncStatus
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory sync status storage
comprehensive_sync_store: Dict[str, Dict[str, Any]] = {}

# Standard SuccessFactors entities for org structure
SF_ORG_STRUCTURE_ENTITIES = {
    "org_unit": [
        "FOLegalEntity",
        "FODepartment", 
        "FODivision",
        "FOBusinessUnit",
        "FOCostCenter"
    ],
    "position": ["Position"],
    "employee": ["PerPerson", "User"]
}

async def run_comprehensive_sync_task(
    sync_id: str,
    connection_id: str,
    include_custom_mdf: bool = False,
    custom_mdf_objects: Optional[List[str]] = None,
    limit_per_entity: Optional[int] = None
):
    """Background task to sync all SuccessFactors org structure entities"""
    try:
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            sync_service = SyncService(db)
            
            all_results = []
            total_records = 0
            processed_records = 0
            failed_records = 0
            errors = []
            
            # Update status to running
            comprehensive_sync_store[sync_id].update({
                "status": SyncStatus.RUNNING,
                "started_at": datetime.utcnow()
            })
            
            # Sync all standard entities
            for target_entity_type, source_entities in SF_ORG_STRUCTURE_ENTITIES.items():
                for source_entity in source_entities:
                    try:
                        logger.info(f"Syncing {source_entity} -> {target_entity_type}")
                        
                        result = await sync_service.sync_entity(
                            connection_id,
                            target_entity_type,
                            source_entity,
                            limit_per_entity
                        )
                        
                        all_results.append(result)
                        
                        if result["success"]:
                            total_records += result["records_fetched"]
                            # Send to org-service
                            from app.routers.sync import send_to_org_service
                            if await send_to_org_service(target_entity_type, result["data"]):
                                processed_records += result["records_fetched"]
                            else:
                                failed_records += result["records_fetched"]
                                errors.append(f"Failed to send {source_entity} to org-service")
                        else:
                            failed_records += result.get("records_fetched", 0)
                            errors.append(f"{source_entity}: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        logger.error(f"Error syncing {source_entity}: {str(e)}")
                        errors.append(f"{source_entity}: {str(e)}")
                        failed_records += 1
            
            # Sync custom MDF objects if requested
            if include_custom_mdf and custom_mdf_objects:
                for mdf_object in custom_mdf_objects:
                    try:
                        logger.info(f"Syncing custom MDF object: {mdf_object}")
                        
                        # Determine target entity type (default to org_unit for custom objects)
                        result = await sync_service.sync_entity(
                            connection_id,
                            "org_unit",  # Default target type for custom MDF
                            mdf_object,
                            limit_per_entity
                        )
                        
                        all_results.append(result)
                        
                        if result["success"]:
                            total_records += result["records_fetched"]
                            from app.routers.sync import send_to_org_service
                            if await send_to_org_service("org_unit", result["data"]):
                                processed_records += result["records_fetched"]
                            else:
                                failed_records += result["records_fetched"]
                                errors.append(f"Failed to send {mdf_object} to org-service")
                        else:
                            failed_records += result.get("records_fetched", 0)
                            errors.append(f"{mdf_object}: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        logger.error(f"Error syncing custom MDF {mdf_object}: {str(e)}")
                        errors.append(f"{mdf_object}: {str(e)}")
            
            # Update final status
            comprehensive_sync_store[sync_id].update({
                "status": SyncStatus.COMPLETED if failed_records == 0 else SyncStatus.FAILED,
                "total_records": total_records,
                "processed_records": processed_records,
                "failed_records": failed_records,
                "errors": errors,
                "results": all_results,
                "completed_at": datetime.utcnow()
            })
            
            # Update connection last_sync_at
            from sqlalchemy import text
            update_query = text("""
                UPDATE hris_connection
                SET last_sync_at = :sync_time,
                    last_sync_status = :sync_status
                WHERE id = :connection_id
            """)
            await db.execute(
                update_query,
                {
                    "sync_time": datetime.utcnow(),
                    "sync_status": "completed" if failed_records == 0 else "failed",
                    "connection_id": connection_id
                }
            )
            await db.commit()
            
    except Exception as e:
        logger.error(f"Comprehensive sync task error: {str(e)}")
        comprehensive_sync_store[sync_id].update({
            "status": SyncStatus.FAILED,
            "errors": [str(e)],
            "completed_at": datetime.utcnow()
        })

@router.post("/comprehensive-sync/start")
async def start_comprehensive_sync(
    connection_id: str,
    include_custom_mdf: bool = False,
    custom_mdf_objects: Optional[List[str]] = None,
    limit_per_entity: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Start comprehensive sync of all SuccessFactors org structure entities
    
    Syncs:
    - FOLegalEntity, FODepartment, FODivision, FOBusinessUnit, FOCostCenter -> org_unit
    - Position -> position
    - PerPerson, User -> employee
    - Custom MDF objects (if specified) -> org_unit
    """
    sync_id = str(uuid.uuid4())
    
    # Initialize sync status
    comprehensive_sync_store[sync_id] = {
        "sync_id": sync_id,
        "status": SyncStatus.PENDING,
        "started_at": datetime.utcnow(),
        "connection_id": connection_id,
        "include_custom_mdf": include_custom_mdf,
        "custom_mdf_objects": custom_mdf_objects or [],
        "total_records": 0,
        "processed_records": 0,
        "failed_records": 0,
        "errors": []
    }
    
    # Start background task
    background_tasks.add_task(
        run_comprehensive_sync_task,
        sync_id,
        connection_id,
        include_custom_mdf,
        custom_mdf_objects,
        limit_per_entity
    )
    
    return {
        "sync_id": sync_id,
        "status": SyncStatus.PENDING,
        "started_at": datetime.utcnow(),
        "connection_id": connection_id,
        "message": "Comprehensive sync started. This will sync all SuccessFactors org structure entities.",
        "entities_to_sync": {
            "org_units": SF_ORG_STRUCTURE_ENTITIES["org_unit"],
            "positions": SF_ORG_STRUCTURE_ENTITIES["position"],
            "employees": SF_ORG_STRUCTURE_ENTITIES["employee"],
            "custom_mdf": custom_mdf_objects if include_custom_mdf else []
        }
    }

@router.get("/comprehensive-sync/{sync_id}")
async def get_comprehensive_sync_status(
    sync_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive sync job status"""
    if sync_id not in comprehensive_sync_store:
        raise HTTPException(status_code=404, detail="Sync job not found")
    
    status_data = comprehensive_sync_store[sync_id]
    return {
        "sync_id": status_data["sync_id"],
        "status": status_data["status"],
        "started_at": status_data["started_at"],
        "connection_id": status_data["connection_id"],
        "total_records": status_data.get("total_records", 0),
        "processed_records": status_data.get("processed_records", 0),
        "failed_records": status_data.get("failed_records", 0),
        "errors": status_data.get("errors", []),
        "results": status_data.get("results", []),
        "completed_at": status_data.get("completed_at")
    }

@router.get("/comprehensive-sync/")
async def list_comprehensive_syncs(
    connection_id: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List all comprehensive sync jobs"""
    results = []
    for sync_id, status_data in list(comprehensive_sync_store.items())[-limit:]:
        if connection_id and status_data.get("connection_id") != connection_id:
            continue
        
        results.append({
            "sync_id": status_data["sync_id"],
            "status": status_data["status"],
            "started_at": status_data["started_at"],
            "connection_id": status_data["connection_id"],
            "total_records": status_data.get("total_records", 0),
            "processed_records": status_data.get("processed_records", 0),
            "failed_records": status_data.get("failed_records", 0),
            "completed_at": status_data.get("completed_at")
        })
    
    return results
