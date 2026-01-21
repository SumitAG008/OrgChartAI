"""
Setup script to create HRIS field mapping tables
Run this to create the necessary database tables for storing field mappings
"""

import asyncio
import asyncpg
import os
from urllib.parse import urlparse
import ssl

async def setup_mapping_tables():
    """Create HRIS field mapping tables in PostgreSQL"""
    
    # Get database URL from environment or config
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Try to read from config file
        try:
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'hris-service'))
            from app.config import settings
            database_url = settings.DATABASE_URL
        except:
            database_url = input("Enter your PostgreSQL DATABASE_URL: ").strip()
            if not database_url:
                print("ERROR: DATABASE_URL is required")
                return
    
    # Parse database URL
    parsed = urlparse(database_url)
    
    # Extract connection parameters
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = parsed.username or "postgres"
    password = parsed.password or ""
    database = parsed.path.lstrip("/") or "postgres"
    
    print(f"Connecting to database: {host}:{port}/{database}")
    
    # SSL context for Neon
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl=ssl_context
        )
        
        print("✅ Connected to database")
        
        # Read and execute schema file
        schema_file = "database/hris_mapping_schema.sql"
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Execute schema
            await conn.execute(schema_sql)
            print(f"✅ Created tables from {schema_file}")
        else:
            # Create tables directly if file doesn't exist
            print("⚠️  Schema file not found, creating tables directly...")
            
            create_tables_sql = """
            -- Field Mappings Table
            CREATE TABLE IF NOT EXISTS hris_field_mapping (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
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
            
            await conn.execute(create_tables_sql)
            print("✅ Created hris_field_mapping and hris_mapping_config tables")
        
        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('hris_field_mapping', 'hris_mapping_config')
        """)
        
        if tables:
            print(f"\n✅ Tables created successfully:")
            for table in tables:
                print(f"   - {table['table_name']}")
        else:
            print("⚠️  Warning: Tables may not have been created")
        
        await conn.close()
        print("\n✅ Setup complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease check:")
        print("1. Database URL is correct")
        print("2. Database is accessible")
        print("3. You have CREATE TABLE permissions")
        raise

if __name__ == "__main__":
    print("Setting up HRIS field mapping tables...\n")
    asyncio.run(setup_mapping_tables())
