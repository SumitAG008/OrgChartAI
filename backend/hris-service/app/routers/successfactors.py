"""
SuccessFactors-specific endpoints
Updated to use proper SF data models and transformer
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.models import (
    SuccessFactorsCredentials, SuccessFactorsConnectionTest
)
from app.services.successfactors_client import SuccessFactorsClient
from app.services.sf_data_transformer import SFDataTransformer
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# ============================================
# Connection Testing
# ============================================

@router.post("/test-connection", response_model=SuccessFactorsConnectionTest)
async def test_successfactors_connection(
    credentials: SuccessFactorsCredentials,
    db: AsyncSession = Depends(get_db)
):
    """Test connection to SuccessFactors"""
    try:
        client = SuccessFactorsClient(
            company_id=credentials.company_id,
            username=credentials.username,
            password=credentials.password,
            api_url=credentials.api_url
        )

        result = await client.test_connection()

        return SuccessFactorsConnectionTest(
            success=result["success"],
            message=result["message"],
            api_version=result.get("api_version")
        )
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return SuccessFactorsConnectionTest(
            success=False,
            message=f"Connection error: {str(e)}"
        )

# ============================================
# Foundation Objects (Org Structure)
# ============================================

@router.get("/business-units")
async def get_business_units(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Business Units from SuccessFactors

    Entity: FOBusinessUnit
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        # Build query parameters
        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        # Fetch from SuccessFactors
        result = await client._make_request("FOBusinessUnit", params=params)

        # Transform data
        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_org_units(raw_data, entity_type="FOBusinessUnit")

        return {
            "count": len(transformed),
            "entity_type": "FOBusinessUnit",
            "business_units": transformed,
            "total_available": result.get("d", {}).get("__count") if isinstance(result.get("d"), dict) else None
        }
    except Exception as e:
        logger.error(f"Error fetching business units: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching business units: {str(e)}"
        )

@router.get("/departments")
async def get_departments(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Departments from SuccessFactors

    Entity: FODepartment
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("FODepartment", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_org_units(raw_data, entity_type="FODepartment")

        return {
            "count": len(transformed),
            "entity_type": "FODepartment",
            "departments": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching departments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching departments: {str(e)}"
        )

@router.get("/divisions")
async def get_divisions(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Divisions from SuccessFactors

    Entity: FODivision
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("FODivision", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_org_units(raw_data, entity_type="FODivision")

        return {
            "count": len(transformed),
            "entity_type": "FODivision",
            "divisions": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching divisions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching divisions: {str(e)}"
        )

@router.get("/cost-centers")
async def get_cost_centers(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Cost Centers from SuccessFactors

    Entity: FOCostCenter
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("FOCostCenter", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)

        # Transform (using entity transformation)
        transformed = []
        for item in raw_data:
            transformed_item = transformer.transform_entity(item, "FOCostCenter")
            transformed.append(transformed_item)

        return {
            "count": len(transformed),
            "entity_type": "FOCostCenter",
            "cost_centers": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching cost centers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching cost centers: {str(e)}"
        )

@router.get("/legal-entities")
async def get_legal_entities(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Legal Entities from SuccessFactors

    Entity: FOLegalEntity
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("FOLegalEntity", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)

        transformed = []
        for item in raw_data:
            transformed_item = transformer.transform_entity(item, "FOLegalEntity")
            transformed.append(transformed_item)

        return {
            "count": len(transformed),
            "entity_type": "FOLegalEntity",
            "legal_entities": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching legal entities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching legal entities: {str(e)}"
        )

@router.get("/locations")
async def get_locations(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Locations from SuccessFactors

    Entity: FOLocation
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("FOLocation", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)

        transformed = []
        for item in raw_data:
            transformed_item = transformer.transform_entity(item, "FOLocation")
            transformed.append(transformed_item)

        return {
            "count": len(transformed),
            "entity_type": "FOLocation",
            "locations": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching locations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching locations: {str(e)}"
        )

# ============================================
# Employee Data
# ============================================

@router.get("/users")
async def get_users(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Users (Employees) from SuccessFactors

    Entity: User
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("User", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_employees(raw_data)

        return {
            "count": len(transformed),
            "entity_type": "User",
            "users": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

# ============================================
# Position Data
# ============================================

@router.get("/positions")
async def get_positions(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch Positions from SuccessFactors

    Entity: Position
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter

        result = await client._make_request("Position", params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_positions(raw_data)

        return {
            "count": len(transformed),
            "entity_type": "Position",
            "positions": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching positions: {str(e)}"
        )

# ============================================
# Legacy/Compatibility Endpoints
# ============================================

@router.get("/org-units")
async def get_org_units(
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    entity_type: str = Query("FOBusinessUnit", description="FOBusinessUnit, FODepartment, or FODivision"),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch org units from SuccessFactors (flexible endpoint)

    Can fetch FOBusinessUnit, FODepartment, or FODivision
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }

        result = await client._make_request(entity_type, params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)
        transformed = transformer.transform_org_units(raw_data, entity_type=entity_type)

        return {
            "count": len(transformed),
            "entity_type": entity_type,
            "org_units": transformed
        }
    except Exception as e:
        logger.error(f"Error fetching org units: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching org units ({entity_type}): {str(e)}"
        )

# ============================================
# Custom/Generic Endpoint
# ============================================

@router.get("/custom-entity/{entity_name}")
async def get_custom_entity(
    entity_name: str,
    company_id: str,
    username: str,
    password: str,
    api_url: Optional[str] = None,
    limit: int = Query(100, le=1000),
    skip: int = Query(0, ge=0),
    filter: Optional[str] = None,
    select: Optional[str] = None,
    expand: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch any entity from SuccessFactors by name

    Useful for custom MDF objects or entities not covered by specific endpoints
    """
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )

        params = {
            "$top": limit,
            "$skip": skip
        }
        if filter:
            params["$filter"] = filter
        if select:
            params["$select"] = select
        if expand:
            params["$expand"] = expand

        result = await client._make_request(entity_name, params=params)

        transformer = SFDataTransformer()
        raw_data = transformer.extract_odata_results(result)

        return {
            "count": len(raw_data),
            "entity_name": entity_name,
            "data": raw_data
        }
    except Exception as e:
        logger.error(f"Error fetching custom entity {entity_name}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching {entity_name}: {str(e)}"
        )
