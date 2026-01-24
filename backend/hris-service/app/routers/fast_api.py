"""
Low-latency API endpoints optimized for SLA requirements
- 100ms SLA: Use cached=true (default)
- 1000ms SLA: Can use cached=false for fresh data
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.successfactors_client import SuccessFactorsClient
from app.services.fast_sync import FastSyncService, warmup_cache
from app.services.cache import hris_cache
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/fast/entities/{entity_type}")
async def get_entity_fast(
    entity_type: str,
    connection_id: str,
    company_id: str,
    username: str,
    password: str,
    api_url: str = "https://api.successfactors.eu",
    cached: bool = Query(True, description="Use cache for 100ms SLA"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fast entity retrieval with SLA guarantees

    - cached=true (default): ~10-50ms response (from cache)
    - cached=false: ~500-2000ms response (fresh from SF)

    For 100ms SLA: Always use cached=true and run cache warmup periodically
    """
    start_time = datetime.utcnow()

    try:
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
            use_cache=cached
        )

        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            "success": True,
            "entity_type": entity_type,
            "count": result["count"],
            "data": result["data"],
            "from_cache": result["from_cache"],
            "elapsed_ms": elapsed,
            "sla_met": elapsed < (100 if cached else 1000)
        }

    except Exception as e:
        logger.error(f"Fast API error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fast/all")
async def get_all_entities_parallel(
    connection_id: str,
    company_id: str,
    username: str,
    password: str,
    api_url: str = "https://api.successfactors.eu",
    entities: str = Query("FODepartment,Position,User", description="Comma-separated entity list"),
    cached: bool = Query(True, description="Use cache"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch multiple entities in parallel

    Even without cache, parallel fetching reduces total latency significantly
    """
    start_time = datetime.utcnow()
    entity_list = [e.strip() for e in entities.split(",")]

    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        if not await client.authenticate():
            raise HTTPException(status_code=401, detail="Authentication failed")

        service = FastSyncService(client)
        result = await service.fetch_all_entities_parallel(
            entity_types=entity_list,
            connection_id=connection_id,
            use_cache=cached
        )

        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000

        return {
            "success": True,
            "entities_fetched": list(result["data"].keys()),
            "total_records": sum(len(v) for v in result["data"].values()),
            "data": result["data"],
            "errors": result["errors"],
            "elapsed_ms": elapsed,
            "parallel": True
        }

    except Exception as e:
        logger.error(f"Parallel fetch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fast/warmup")
async def warmup_entity_cache(
    connection_id: str,
    company_id: str,
    username: str,
    password: str,
    api_url: str = "https://api.successfactors.eu",
    db: AsyncSession = Depends(get_db)
):
    """
    Pre-warm cache for fast subsequent requests

    Call this:
    - On application startup
    - Periodically via cron (every 5-10 minutes)
    - After data changes in SuccessFactors
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        if not await client.authenticate():
            raise HTTPException(status_code=401, detail="Authentication failed")

        result = await warmup_cache(client, connection_id)

        return {
            "success": True,
            "message": "Cache warmed up successfully",
            "elapsed_ms": result["elapsed_ms"],
            "entities_cached": list(result["data"].keys())
        }

    except Exception as e:
        logger.error(f"Cache warmup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/fast/cache")
async def clear_cache():
    """Clear all cached data"""
    await hris_cache.clear()
    return {"success": True, "message": "Cache cleared"}


@router.get("/fast/health")
async def health_check():
    """
    Health check with latency measurement
    Use this to monitor if SLA is being met
    """
    start = datetime.utcnow()
    # Simulate minimal work
    await hris_cache.get("health_check")
    elapsed = (datetime.utcnow() - start).total_seconds() * 1000

    return {
        "status": "healthy",
        "cache_latency_ms": elapsed,
        "timestamp": datetime.utcnow().isoformat()
    }
