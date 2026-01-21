"""
Quick setup script to create HRIS field mapping tables
Uses the same database connection as the hris-service
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

async def setup_tables():
    """Create HRIS field mapping tables"""
    
    print("Setting up HRIS field mapping tables...\n")
    
    # Fix Windows console encoding
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    # Read the schema file
    schema_file = os.path.join(os.path.dirname(__file__), "..", "..", "database", "hris_mapping_schema.sql")
    
    if not os.path.exists(schema_file):
        print(f"⚠️  Schema file not found at: {schema_file}")
        print("Creating tables directly...\n")
        
        # Create tables directly
        create_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- Field Mappings Table
        CREATE TABLE IF NOT EXISTS hris_field_mapping (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            connection_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            source_field TEXT NOT NULL,
            target_field TEXT NOT NULL,
            mapping_type TEXT NOT NULL DEFAULT 'direct',
            transform_function TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT,
            UNIQUE(connection_id, entity_type, source_field)
        );

        CREATE INDEX IF NOT EXISTS idx_hris_mapping_connection ON hris_field_mapping(connection_id);
        CREATE INDEX IF NOT EXISTS idx_hris_mapping_entity_type ON hris_field_mapping(connection_id, entity_type);
        CREATE INDEX IF NOT EXISTS idx_hris_mapping_active ON hris_field_mapping(connection_id, entity_type, is_active);

        -- Mapping Configuration
        CREATE TABLE IF NOT EXISTS hris_mapping_config (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            connection_id TEXT NOT NULL UNIQUE,
            target_entity_type TEXT NOT NULL,
            source_entity_name TEXT NOT NULL,
            hris_source TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            last_synced_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            created_by TEXT,
            updated_by TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_mapping_config_connection ON hris_mapping_config(connection_id);
        CREATE INDEX IF NOT EXISTS idx_mapping_config_active ON hris_mapping_config(connection_id, is_active);
        """
    else:
        print(f"Reading schema from: {schema_file}\n")
        with open(schema_file, 'r') as f:
            create_sql = f.read()
    
    try:
        # Execute statements one by one in separate transactions
        async with engine.connect() as conn:
            # Better SQL parsing - split by semicolon but keep multi-line statements together
            # Remove comments first
            lines = []
            for line in create_sql.split('\n'):
                # Remove inline comments
                if '--' in line:
                    line = line[:line.index('--')]
                line = line.strip()
                if line:
                    lines.append(line)
            
            # Join and split by semicolon
            sql_text = ' '.join(lines)
            statements = [s.strip() for s in sql_text.split(';') if s.strip()]
            
            # Execute each statement
            for statement in statements:
                if not statement:
                    continue
                try:
                    async with conn.begin():
                        await conn.execute(text(statement))
                        print(f"Executed: {statement.split()[0:3]}...")
                except Exception as e:
                    # Ignore "already exists" errors
                    error_str = str(e).lower()
                    if "already exists" in error_str or "duplicate" in error_str:
                        print(f"Skipped (already exists): {statement.split()[0:3]}...")
                    elif "does not exist" in error_str and "index" in error_str.lower():
                        # Index creation failed because table doesn't exist yet - this is OK, will retry
                        print(f"Deferred (table not ready): {statement.split()[0:3]}...")
                    else:
                        print(f"Warning: {statement.split()[0:3]}... - {str(e)[:100]}")
            
            print("\nExecuting CREATE TABLE statements directly...")
            
            # Create tables directly with proper syntax
            create_table1 = """
            CREATE TABLE IF NOT EXISTS hris_field_mapping (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                connection_id TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                source_field TEXT NOT NULL,
                target_field TEXT NOT NULL,
                mapping_type TEXT NOT NULL DEFAULT 'direct',
                transform_function TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_by TEXT,
                UNIQUE(connection_id, entity_type, source_field)
            )
            """
            
            create_table2 = """
            CREATE TABLE IF NOT EXISTS hris_mapping_config (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                connection_id TEXT NOT NULL UNIQUE,
                target_entity_type TEXT NOT NULL,
                source_entity_name TEXT NOT NULL,
                hris_source TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                last_synced_at TIMESTAMP,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                updated_by TEXT
            )
            """
            
            # Create tables
            for create_stmt in [create_table1, create_table2]:
                try:
                    async with conn.begin():
                        await conn.execute(text(create_stmt))
                        print("Created table successfully")
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" not in error_str:
                        print(f"Error creating table: {str(e)[:200]}")
            
            # Create indexes
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_hris_mapping_connection ON hris_field_mapping(connection_id)",
                "CREATE INDEX IF NOT EXISTS idx_hris_mapping_entity_type ON hris_field_mapping(connection_id, entity_type)",
                "CREATE INDEX IF NOT EXISTS idx_hris_mapping_active ON hris_field_mapping(connection_id, entity_type, is_active)",
                "CREATE INDEX IF NOT EXISTS idx_mapping_config_connection ON hris_mapping_config(connection_id)",
                "CREATE INDEX IF NOT EXISTS idx_mapping_config_active ON hris_mapping_config(connection_id, is_active)"
            ]
            
            for index_sql in indexes:
                try:
                    async with conn.begin():
                        await conn.execute(text(index_sql))
                except Exception as e:
                    error_str = str(e).lower()
                    if "already exists" not in error_str and "does not exist" not in error_str:
                        print(f"Warning creating index: {str(e)[:100]}")
            
            print("\nTables created successfully!")
            
            # Verify tables exist
            async with conn.begin():
                result = await conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('hris_field_mapping', 'hris_mapping_config')
                """))
                
                tables = result.fetchall()
                if tables:
                    print(f"\nVerified tables exist:")
                    for table in tables:
                        print(f"   - {table[0]}")
                else:
                    print("Warning: Could not verify tables")
        
        print("\nSetup complete! You can now save mappings.")
        
    except Exception as e:
        print(f"\nError creating tables: {e}")
        print("\nTroubleshooting:")
        print("1. Check your DATABASE_URL in app/config.py")
        print("2. Ensure you have CREATE TABLE permissions")
        print("3. Verify database connection")
        raise

if __name__ == "__main__":
    asyncio.run(setup_tables())
