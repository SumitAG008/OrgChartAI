"""
Audit Service
Manages audit trails and version history
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

class AuditService:
    """Service for managing audit trails"""
    
    async def get_change_history(
        self,
        db: AsyncSession,
        table_name: str,
        record_id: UUID,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get change history for a record"""
        query = text("""
            SELECT * FROM get_change_history(:table_name, :record_id, :limit)
        """)
        
        result = await db.execute(
            query,
            {"table_name": table_name, "record_id": str(record_id), "limit": limit}
        )
        
        return [dict(row) for row in result]
    
    async def get_version_at_timestamp(
        self,
        db: AsyncSession,
        table_name: str,
        record_id: UUID,
        timestamp: datetime
    ) -> Optional[Dict[str, Any]]:
        """Get version of record at specific timestamp"""
        query = text("""
            SELECT get_version_at_timestamp(:table_name, :record_id, :timestamp) as data
        """)
        
        result = await db.execute(
            query,
            {
                "table_name": table_name,
                "record_id": str(record_id),
                "timestamp": timestamp
            }
        )
        
        row = result.first()
        if row and row.data:
            return row.data
        return None
    
    async def get_all_changes_today(
        self,
        db: AsyncSession,
        user_id: Optional[UUID] = None
    ) -> List[Dict[str, Any]]:
        """Get all changes made today"""
        query = text("""
            SELECT 
                table_name,
                record_id,
                action,
                changed_fields,
                changed_by,
                changed_at
            FROM change_history
            WHERE DATE(changed_at) = CURRENT_DATE
            AND (:user_id IS NULL OR changed_by = :user_id)
            ORDER BY changed_at DESC
        """)
        
        result = await db.execute(
            query,
            {"user_id": str(user_id) if user_id else None}
        )
        
        return [dict(row) for row in result]
    
    async def get_change_summary(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get summary of changes in date range"""
        query = text("""
            SELECT 
                COUNT(*) as total_changes,
                COUNT(DISTINCT table_name) as tables_affected,
                COUNT(DISTINCT record_id) as records_changed,
                COUNT(DISTINCT changed_by) as users_active
            FROM change_history
            WHERE changed_at BETWEEN :start_date AND :end_date
        """)
        
        result = await db.execute(
            query,
            {"start_date": start_date, "end_date": end_date}
        )
        
        row = result.first()
        return dict(row) if row else {}
