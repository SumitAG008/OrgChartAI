"""
Script to create HRIS service database tables
Run this if tables don't exist after service startup
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_tables():
    """Create all HRIS service tables"""
    logger.info("Creating HRIS service tables...")
    
    statements = [
        # Enable UUID extension
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"",
        
        # HRIS Connections Table
        """CREATE TABLE IF NOT EXISTS hris_connection (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            system TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            description TEXT,
            credentials JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            last_sync_at TIMESTAMP,
            last_sync_status TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""",
        
        # Field Mappings Table
        """CREATE TABLE IF NOT EXISTS hris_field_mapping (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            connection_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            source_entity_name TEXT,
            source_field TEXT NOT NULL,
            target_field TEXT NOT NULL,
            mapping_type TEXT NOT NULL DEFAULT 'direct',
            transform_function TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )""",
        
        # Mapping Configuration
        """CREATE TABLE IF NOT EXISTS hris_mapping_config (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            connection_id TEXT NOT NULL,
            target_entity_type TEXT NOT NULL,
            source_entity_name TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        )""",
        
        # Indexes
        "CREATE INDEX IF NOT EXISTS idx_hris_connection_active ON hris_connection(is_active)",
        "CREATE INDEX IF NOT EXISTS idx_hris_connection_system ON hris_connection(system)",
        "CREATE INDEX IF NOT EXISTS idx_hris_mapping_connection ON hris_field_mapping(connection_id)",
        "CREATE INDEX IF NOT EXISTS idx_hris_mapping_entity_type ON hris_field_mapping(connection_id, entity_type)",
        "CREATE INDEX IF NOT EXISTS idx_hris_mapping_active ON hris_field_mapping(connection_id, entity_type, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_mapping_config_connection ON hris_mapping_config(connection_id)",
        "CREATE INDEX IF NOT EXISTS idx_mapping_config_active ON hris_mapping_config(connection_id, is_active)",
    ]
    
    try:
        async with engine.begin() as conn:
            # Test connection first
            await conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            
            # Execute each statement
            for i, statement in enumerate(statements, 1):
                try:
                    await conn.execute(text(statement))
                    logger.info(f"✓ Statement {i}/{len(statements)} executed successfully")
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" in error_str or "duplicate" in error_str:
                        logger.info(f"⚠ Statement {i} skipped (already exists)")
                    else:
                        logger.error(f"✗ Statement {i} failed: {str(e)[:200]}")
                        raise
            
            # Verify tables exist
            logger.info("\nVerifying tables...")
            check_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('hris_connection', 'hris_field_mapping', 'hris_mapping_config')
                ORDER BY table_name
            """)
            result = await conn.execute(check_query)
            tables = result.fetchall()
            
            if tables:
                logger.info("✓ Tables verified:")
                for table in tables:
                    logger.info(f"  - {table[0]}")
            else:
                logger.warning("⚠ No tables found - check database connection")
            
            logger.info("\n✅ Table creation complete!")
            
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(create_tables())
