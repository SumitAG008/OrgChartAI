"""
SuccessFactors-specific endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import (
    SuccessFactorsCredentials, SuccessFactorsConnectionTest
)
from app.services.successfactors_client import SuccessFactorsClient
from app.services.data_transformer import DataTransformer

router = APIRouter()

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
        return SuccessFactorsConnectionTest(
            success=False,
            message=f"Connection error: {str(e)}"
        )

@router.get("/users")
async def get_users(
    company_id: str,
    username: str,
    password: str,
    api_url: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Fetch users from SuccessFactors (for testing)"""
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )
        
        users = await client.get_users(top=limit)
        transformed = DataTransformer.transform_users(users)
        
        return {
            "count": len(transformed),
            "users": transformed
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.get("/positions")
async def get_positions(
    company_id: str,
    username: str,
    password: str,
    api_url: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Fetch positions from SuccessFactors (for testing)"""
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )
        
        positions = await client.get_positions(top=limit)
        transformed = DataTransformer.transform_positions(positions)
        
        return {
            "count": len(transformed),
            "positions": transformed
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching positions: {str(e)}"
        )

@router.get("/org-units")
async def get_org_units(
    company_id: str,
    username: str,
    password: str,
    api_url: str = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Fetch org units from SuccessFactors (for testing)"""
    try:
        client = SuccessFactorsClient(
            company_id=company_id,
            username=username,
            password=password,
            api_url=api_url
        )
        
        org_units = await client.get_org_units(top=limit)
        transformed = DataTransformer.transform_org_units(org_units)
        
        return {
            "count": len(transformed),
            "org_units": transformed
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching org units: {str(e)}"
        )
