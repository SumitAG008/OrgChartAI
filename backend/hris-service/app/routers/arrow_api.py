"""
Apache Arrow API Endpoints

Provides multiple data formats:
1. JSON (for standard UI consumption)
2. Arrow IPC (for Arrow-compatible clients - fastest)
3. Statistics (for monitoring/debugging)
"""

from fastapi import APIRouter, HTTPException, Response, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import logging

from app.services.arrow_service import ArrowService, arrow_store
from app.services.successfactors_client import SuccessFactorsClient
from app.services.fast_sync import FastSyncService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/arrow/sync/{entity_type}")
async def sync_to_arrow(
    entity_type: str,
    connection_id: str,
    company_id: str,
    username: str,
    password: str,
    api_url: str = "https://api.successfactors.eu",
):
    """
    Sync data from SuccessFactors and store as Arrow table

    This is faster than JSON for subsequent reads
    """
    start_time = datetime.utcnow()

    try:
        # Fetch data from SF
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        if not await client.authenticate():
            raise HTTPException(status_code=401, detail="Authentication failed")

        service = FastSyncService(client)
        result = await service.get_entity_fast(
            entity_type=entity_type,
            connection_id=connection_id,
            use_cache=False  # Get fresh data
        )

        # Store as Arrow table
        store_key = f"{connection_id}:{entity_type}"
        # Map SF entity types to our schema types
        schema_type_map = {
            "Position": "position",
            "User": "employee",
            "PerPerson": "employee",
            "FODepartment": "org_unit",
            "FODivision": "org_unit",
            "FOCostCenter": "org_unit",
            "FOBusinessUnit": "org_unit",
        }
        schema_type = schema_type_map.get(entity_type, "org_unit")

        stats = arrow_store.store(store_key, result["data"], schema_type)

        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            "success": True,
            "entity_type": entity_type,
            "store_key": store_key,
            "arrow_stats": stats,
            "elapsed_ms": elapsed,
            "message": f"Stored {stats['num_rows']} records as Arrow table ({stats['memory_mb']} MB)"
        }

    except Exception as e:
        logger.error(f"Arrow sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arrow/data/{store_key:path}")
async def get_arrow_data(
    store_key: str,
    format: str = Query("json", description="Output format: json, arrow, stats"),
    filter_column: Optional[str] = None,
    filter_value: Optional[str] = None,
):
    """
    Get data from Arrow store

    Formats:
    - json: Standard JSON (for UI)
    - arrow: Arrow IPC binary (for Arrow clients)
    - stats: Table statistics only
    """
    table = arrow_store.get(store_key)
    if table is None:
        raise HTTPException(status_code=404, detail=f"No data found for key: {store_key}")

    if format == "stats":
        return ArrowService.get_table_stats(table)

    if format == "arrow":
        # Return Arrow IPC binary format
        ipc_bytes = ArrowService.table_to_ipc_bytes(table)
        return Response(
            content=ipc_bytes,
            media_type="application/vnd.apache.arrow.file",
            headers={
                "Content-Disposition": f"attachment; filename={store_key.replace(':', '_')}.arrow",
                "X-Arrow-Rows": str(table.num_rows),
                "X-Arrow-Bytes": str(table.nbytes),
            }
        )

    # JSON format (default)
    if filter_column and filter_value:
        records = arrow_store.filter(store_key, filter_column, filter_value)
    else:
        records = arrow_store.get_as_records(store_key)

    return {
        "store_key": store_key,
        "count": len(records),
        "data": records,
        "format": "json"
    }


@router.get("/arrow/stores")
async def list_arrow_stores():
    """List all Arrow data stores and their statistics"""
    return arrow_store.stats()


@router.delete("/arrow/data/{store_key:path}")
async def delete_arrow_data(store_key: str):
    """Delete data from Arrow store"""
    if store_key not in arrow_store.keys():
        raise HTTPException(status_code=404, detail=f"No data found for key: {store_key}")

    # We need to add a delete method to ArrowDataStore
    arrow_store._tables.pop(store_key, None)
    return {"success": True, "message": f"Deleted {store_key}"}


@router.post("/arrow/convert")
async def convert_to_arrow(
    entity_type: str,
    records: List[dict],
):
    """
    Convert JSON records to Arrow format

    Use this to test Arrow conversion without SF connection
    """
    try:
        schema_type_map = {
            "position": "position",
            "employee": "employee",
            "org_unit": "org_unit",
        }
        schema_type = schema_type_map.get(entity_type, entity_type)

        table = ArrowService.records_to_arrow(records, schema_type)
        stats = ArrowService.get_table_stats(table)

        # Calculate size comparison
        import json
        json_size = len(json.dumps(records).encode())
        arrow_size = table.nbytes

        return {
            "success": True,
            "arrow_stats": stats,
            "size_comparison": {
                "json_bytes": json_size,
                "arrow_bytes": arrow_size,
                "compression_ratio": round(json_size / max(arrow_size, 1), 2),
                "savings_percent": round((1 - arrow_size / max(json_size, 1)) * 100, 1)
            }
        }

    except Exception as e:
        logger.error(f"Arrow conversion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/arrow/benchmark")
async def arrow_benchmark():
    """
    Benchmark Arrow vs JSON performance

    Shows the speed advantage of Arrow format
    """
    import time
    import json

    # Generate test data
    test_records = [
        {
            "hris_id": f"POS{i:05d}",
            "code": f"CODE{i}",
            "title": f"Position Title {i}",
            "job_code": f"JOB{i % 100}",
            "org_unit_id": f"ORG{i % 50}",
            "status": "Active" if i % 2 == 0 else "Inactive",
            "hris_source": "successfactors",
            "hris_type": "Position",
        }
        for i in range(10000)
    ]

    results = {}

    # Benchmark JSON serialization
    start = time.perf_counter()
    json_bytes = json.dumps(test_records).encode()
    json_serialize_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    json.loads(json_bytes.decode())
    json_deserialize_time = (time.perf_counter() - start) * 1000

    results["json"] = {
        "serialize_ms": round(json_serialize_time, 2),
        "deserialize_ms": round(json_deserialize_time, 2),
        "total_ms": round(json_serialize_time + json_deserialize_time, 2),
        "size_bytes": len(json_bytes),
    }

    # Benchmark Arrow serialization
    start = time.perf_counter()
    table = ArrowService.records_to_arrow(test_records, "position")
    arrow_bytes = ArrowService.table_to_ipc_bytes(table)
    arrow_serialize_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    ArrowService.ipc_bytes_to_table(arrow_bytes)
    arrow_deserialize_time = (time.perf_counter() - start) * 1000

    results["arrow"] = {
        "serialize_ms": round(arrow_serialize_time, 2),
        "deserialize_ms": round(arrow_deserialize_time, 2),
        "total_ms": round(arrow_serialize_time + arrow_deserialize_time, 2),
        "size_bytes": len(arrow_bytes),
    }

    # Calculate speedup
    json_total = results["json"]["total_ms"]
    arrow_total = results["arrow"]["total_ms"]

    return {
        "test_records": len(test_records),
        "results": results,
        "speedup": {
            "arrow_faster_by": f"{round(json_total / max(arrow_total, 0.1), 1)}x",
            "time_saved_ms": round(json_total - arrow_total, 2),
            "size_reduction_percent": round(
                (1 - results["arrow"]["size_bytes"] / max(results["json"]["size_bytes"], 1)) * 100, 1
            ),
        },
        "recommendation": "Use Arrow for datasets > 1000 records"
    }
