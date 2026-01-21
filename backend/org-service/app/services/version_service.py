"""
Version Service
Manages version history and time-travel queries
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

class VersionService:
    """Service for managing version history"""
    
    async def get_all_versions(
        self,
        db: AsyncSession,
        table_name: str,
        record_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all versions of a record"""
        query = text("""
            SELECT 
                version,
                data,
                created_at,
                created_by,
                change_summary
            FROM version_history
            WHERE table_name = :table_name
              AND record_id = :record_id
            ORDER BY version ASC
        """)
        
        result = await db.execute(
            query,
            {"table_name": table_name, "record_id": str(record_id)}
        )
        
        return [dict(row) for row in result]
    
    async def get_version(
        self,
        db: AsyncSession,
        table_name: str,
        record_id: UUID,
        version: int
    ) -> Optional[Dict[str, Any]]:
        """Get specific version of a record"""
        query = text("""
            SELECT data
            FROM version_history
            WHERE table_name = :table_name
              AND record_id = :record_id
              AND version = :version
        """)
        
        result = await db.execute(
            query,
            {"table_name": table_name, "record_id": str(record_id), "version": version}
        )
        
        row = result.first()
        return row.data if row else None
    
    async def restore_version(
        self,
        db: AsyncSession,
        table_name: str,
        record_id: UUID,
        version: int,
        user_id: UUID
    ) -> bool:
        """Restore a record to a specific version"""
        version_data = await self.get_version(db, table_name, record_id, version)
        
        if not version_data:
            return False
        
        # Update current record with version data
        # This will trigger new version creation
        update_query = text(f"""
            UPDATE {table_name}
            SET 
                {', '.join([f"{k} = :{k}" for k in version_data.keys() if k not in ['id', 'created_at', 'version']])},
                updated_by = :user_id,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :record_id
        """)
        
        params = {**version_data, "record_id": str(record_id), "user_id": str(user_id)}
        await db.execute(update_query, params)
        await db.commit()
        
        return True
