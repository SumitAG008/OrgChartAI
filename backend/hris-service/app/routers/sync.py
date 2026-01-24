"""
Data synchronization endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.models import SyncRequest, SyncResponse, SyncStatus
from app.services.sync_service import SyncService
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid
import httpx
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory sync status storage (in production, use Redis or database)
sync_status_store: Dict[str, Dict[str, Any]] = {}

from datetime import datetime as dt_datetime

def serialize_for_json(obj):
    """Convert datetime and other non-JSON-serializable objects to JSON-compatible types"""
    if isinstance(obj, (datetime, dt_datetime)):
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

async def run_sync_task(
    sync_id: str,
    connection_id: str,
    entity_types: List[str],
    limit_per_entity: Optional[int] = None
):
    """Background task to run sync"""
    try:
        # Update status to running
        sync_status_store[sync_id] = {
            "status": SyncStatus.RUNNING,
            "started_at": datetime.utcnow(),
            "connection_id": connection_id,
            "entities": entity_types,
            "processed_records": 0,
            "total_records": 0,
            "failed_records": 0,
            "errors": []
        }
        
        # Get database session
        from app.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                sync_service = SyncService(db)
                
                # Sync all entities
                result = await sync_service.sync_all_entities(
                    connection_id,
                    entity_types,
                    limit_per_entity
                )
                
                # Update status
                total_records = result.get("total_records", 0)
                processed = 0
                failed = 0
                errors = []
                
                # Send data to org-service and track results
                for entity_result in result.get("results", []):
                    if entity_result.get("success"):
                        entity_type = entity_result["entity_type"]
                        data = entity_result.get("data", [])
                        
                        # Send to org-service
                        if await send_to_org_service(entity_type, data):
                            processed += len(data)
                        else:
                            failed += len(data)
                            errors.append(f"Failed to send {entity_type} to org-service")
                    else:
                        failed += entity_result.get("records_fetched", 0)
                        errors.append(
                            f"{entity_result['entity_type']}: {entity_result.get('error', 'Unknown error')}"
                        )
                
                # Update sync status
                sync_status_store[sync_id].update({
                    "status": SyncStatus.COMPLETED if failed == 0 else SyncStatus.FAILED,
                    "processed_records": processed,
                    "total_records": total_records,
                    "failed_records": failed,
                    "errors": errors,
                    "completed_at": datetime.utcnow()
                })
                
                # Update connection last_sync_at
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
                        "sync_status": "completed" if failed == 0 else "failed",
                        "connection_id": connection_id
                    }
                )
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise
    except Exception as e:
        logger.error(f"Sync task error: {str(e)}")
        sync_status_store[sync_id].update({
            "status": SyncStatus.FAILED,
            "errors": [str(e)],
            "completed_at": datetime.utcnow()
        })

@router.post("/start", response_model=SyncResponse)
async def start_sync(
    request: SyncRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start a data synchronization job"""
    sync_id = str(uuid.uuid4())
    
    # Default entities if not specified
    entities = request.entities or ["org_unit", "position", "employee"]
    
    # Initialize sync status
    sync_status_store[sync_id] = {
        "sync_id": sync_id,
        "status": SyncStatus.PENDING,
        "started_at": datetime.utcnow(),
        "connection_id": request.connection_id,
        "entities": entities,
        "total_records": 0,
        "processed_records": 0,
        "failed_records": 0,
        "errors": []
    }
    
    # Start background task
    background_tasks.add_task(
        run_sync_task,
        sync_id,
        request.connection_id,
        entities,
        None  # limit_per_entity
    )
    
    return SyncResponse(
        sync_id=sync_id,
        status=SyncStatus.PENDING,
        started_at=datetime.utcnow(),
        connection_id=request.connection_id,
        entities=entities
    )

@router.get("/{sync_id}", response_model=SyncResponse)
async def get_sync_status(sync_id: str, db: AsyncSession = Depends(get_db)):
    """Get sync job status"""
    if sync_id not in sync_status_store:
        raise HTTPException(status_code=404, detail="Sync job not found")
    
    status_data = sync_status_store[sync_id]
    return SyncResponse(
        sync_id=status_data["sync_id"],
        status=status_data["status"],
        started_at=status_data["started_at"],
        connection_id=status_data["connection_id"],
        entities=status_data["entities"],
        total_records=status_data.get("total_records"),
        processed_records=status_data.get("processed_records"),
        failed_records=status_data.get("failed_records"),
        errors=status_data.get("errors")
    )

@router.get("/", response_model=list[SyncResponse])
async def list_syncs(
    connection_id: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """List sync jobs"""
    results = []
    for sync_id, status_data in list(sync_status_store.items())[:limit]:
        if connection_id and status_data.get("connection_id") != connection_id:
            continue
        
        results.append(SyncResponse(
            sync_id=status_data["sync_id"],
            status=status_data["status"],
            started_at=status_data["started_at"],
            connection_id=status_data["connection_id"],
            entities=status_data["entities"],
            total_records=status_data.get("total_records"),
            processed_records=status_data.get("processed_records"),
            failed_records=status_data.get("failed_records"),
            errors=status_data.get("errors")
        ))
    
    return results
