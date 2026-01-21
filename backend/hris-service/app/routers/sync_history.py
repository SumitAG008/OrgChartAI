"""
Sync History API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db

router = APIRouter(prefix="/connections", tags=["Sync History"])

class SyncHistoryItem(BaseModel):
    id: str
    connection_id: str
    sync_type: str  # 'full', 'incremental'
    status: str  # 'success', 'failed', 'partial'
    records_synced: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    error_message: Optional[str]

@router.get("/{connection_id}/sync-history", response_model=List[Dict[str, Any]])
async def get_sync_history(
    connection_id: str,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Get sync history for a connection"""
    try:
        # Check if table exists
        table_check = text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'hris_sync_history'
            )
        """)
        
        result = await db.execute(table_check)
        table_exists = result.scalar_one()
        
        if not table_exists:
            return []  # Return empty list if table doesn't exist yet
        
        query = text("""
            SELECT 
                id,
                connection_id,
                sync_type,
                status,
                records_synced,
                started_at,
                completed_at,
                EXTRACT(EPOCH FROM (completed_at - started_at)) as duration_seconds,
                error_message
            FROM hris_sync_history
            WHERE connection_id = :connection_id
            ORDER BY started_at DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"connection_id": connection_id, "limit": limit})
        rows = result.fetchall()
        
        history = []
        for row in rows:
            history.append({
                "id": str(row[0]),
                "connection_id": row[1],
                "sync_type": row[2],
                "status": row[3],
                "records_synced": row[4] if isinstance(row[4], dict) else {},
                "started_at": row[5].isoformat() if row[5] else None,
                "completed_at": row[6].isoformat() if row[6] else None,
                "duration_seconds": float(row[7]) if row[7] else None,
                "error_message": row[8]
            })
        
        return history
        
    except Exception as e:
        # Return empty list on error (table might not exist)
        return []
