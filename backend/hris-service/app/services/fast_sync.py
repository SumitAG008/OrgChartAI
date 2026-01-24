"""
Optimized sync service for low-latency requirements
Target: 100ms for cached, 1000ms for fresh data
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
from app.services.cache import hris_cache, cache_key_for_entity
from app.services.successfactors_client import SuccessFactorsClient

logger = logging.getLogger(__name__)


class FastSyncService:
    """High-performance sync service optimized for strict SLAs"""

    def __init__(self, client: SuccessFactorsClient):
        self.client = client

    async def fetch_all_entities_parallel(
        self,
        entity_types: List[str],
        connection_id: str,
        use_cache: bool = True,
        cache_ttl: int = 300
    ) -> Dict[str, Any]:
        """
        Fetch multiple entities in parallel for maximum throughput

        For 100ms SLA: Set use_cache=True
        For 1000ms SLA: Can work without cache for fresh data
        """
        start_time = datetime.utcnow()
        results = {}
        errors = []

        # Define fetch functions for each entity type
        entity_fetchers = {
            "FODepartment": self.client.get_departments,
            "FOCostCenter": self.client.get_cost_centers,
            "FODivision": self.client.get_divisions,
            "FOBusinessUnit": self.client.get_business_units,
            "FOLegalEntity": self.client.get_legal_entities,
            "Position": self.client.get_positions,
            "User": self.client.get_users,
            "PerPerson": self.client.get_per_person,
        }

        async def fetch_entity(entity_type: str) -> tuple:
            """Fetch single entity with caching"""
            cache_key = cache_key_for_entity(entity_type, connection_id)

            # Check cache first
            if use_cache:
                cached = await hris_cache.get(cache_key)
                if cached is not None:
                    logger.info(f"Cache HIT for {entity_type} - 0ms")
                    return (entity_type, cached, None)

            # Fetch fresh data
            fetcher = entity_fetchers.get(entity_type)
            if not fetcher:
                return (entity_type, [], f"Unknown entity type: {entity_type}")

            try:
                entity_start = datetime.utcnow()
                data = await fetcher(top=1000)
                elapsed = (datetime.utcnow() - entity_start).total_seconds() * 1000
                logger.info(f"Fetched {entity_type}: {len(data)} records in {elapsed:.0f}ms")

                # Cache the result
                if use_cache:
                    await hris_cache.set(cache_key, data, cache_ttl)

                return (entity_type, data, None)
            except Exception as e:
                logger.error(f"Error fetching {entity_type}: {e}")
                return (entity_type, [], str(e))

        # Fetch all entities in parallel
        tasks = [fetch_entity(et) for et in entity_types if et in entity_fetchers]
        fetch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in fetch_results:
            if isinstance(result, Exception):
                errors.append(str(result))
            else:
                entity_type, data, error = result
                results[entity_type] = data
                if error:
                    errors.append(error)

        elapsed_total = (datetime.utcnow() - start_time).total_seconds() * 1000
        logger.info(f"Total parallel fetch: {elapsed_total:.0f}ms for {len(entity_types)} entities")

        return {
            "data": results,
            "errors": errors,
            "elapsed_ms": elapsed_total,
            "cached": use_cache
        }

    async def get_entity_fast(
        self,
        entity_type: str,
        connection_id: str,
        use_cache: bool = True,
        cache_ttl: int = 60  # Shorter TTL for single entity
    ) -> Dict[str, Any]:
        """
        Get single entity with aggressive caching

        For 100ms SLA: This should hit cache most of the time
        """
        start_time = datetime.utcnow()
        cache_key = cache_key_for_entity(entity_type, connection_id)

        # Check cache
        if use_cache:
            cached = await hris_cache.get(cache_key)
            if cached is not None:
                elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
                return {
                    "entity_type": entity_type,
                    "data": cached,
                    "count": len(cached),
                    "elapsed_ms": elapsed,
                    "from_cache": True
                }

        # Fetch fresh
        fetchers = {
            "Position": self.client.get_positions,
            "User": self.client.get_users,
            "FODepartment": self.client.get_departments,
        }

        fetcher = fetchers.get(entity_type)
        if not fetcher:
            raise ValueError(f"Unknown entity type: {entity_type}")

        data = await fetcher(top=1000)

        if use_cache:
            await hris_cache.set(cache_key, data, cache_ttl)

        elapsed = (datetime.utcnow() - start_time).total_seconds() * 1000
        return {
            "entity_type": entity_type,
            "data": data,
            "count": len(data),
            "elapsed_ms": elapsed,
            "from_cache": False
        }


async def warmup_cache(client: SuccessFactorsClient, connection_id: str):
    """
    Pre-warm cache for fast subsequent requests
    Call this on startup or periodically in background
    """
    service = FastSyncService(client)
    entities = ["FODepartment", "FOCostCenter", "Position", "User"]

    logger.info("Warming up cache...")
    result = await service.fetch_all_entities_parallel(
        entities,
        connection_id,
        use_cache=True,
        cache_ttl=600  # 10 minute TTL for warmup
    )
    logger.info(f"Cache warmup complete in {result['elapsed_ms']:.0f}ms")
    return result
