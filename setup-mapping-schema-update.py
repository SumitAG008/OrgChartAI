"""
Update HRIS mapping schema to support multiple source entities per target
"""

import asyncio
import asyncpg
import os
import sys
from urllib.parse import urlparse
import ssl

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def update_schema():
    # Try to get DATABASE_URL from backend config
    import sys
    script_dir = os.path.dirname(__file__)
    sys.path.insert(0, os.path.join(script_dir, "backend", "hris-service"))
    
    try:
        from app.config import settings
        database_url = settings.DATABASE_URL
    except:
        # Fallback to environment variable
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("DATABASE_URL not found")
            print("Please set DATABASE_URL environment variable or ensure backend/hris-service/app/config.py has DATABASE_URL")
            return
    
    # Parse database URL
    parsed = urlparse(database_url)
    host = parsed.hostname
    port = parsed.port or 5432
    user = parsed.username
    password = parsed.password
    database = parsed.path[1:] if parsed.path.startswith('/') else parsed.path
    
    # Create SSL context for Neon
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        conn = await asyncpg.connect(
            host=host, port=port, user=user, password=password, database=database, ssl=ssl_context
        )
        print("Connected to database")
        
        # Read SQL update script
        script_dir = os.path.dirname(__file__)
        schema_file_path = os.path.join(script_dir, "database", "hris_mapping_schema_update.sql")
        
        with open(schema_file_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute the schema update SQL
        await conn.execute(schema_sql)
        print("Successfully executed schema update")
        
        # Verify the changes
        result = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'hris_field_mapping' 
            AND column_name = 'source_entity_name'
        """)
        
        if result:
            print("Verified: source_entity_name column exists in hris_field_mapping")
        else:
            print("Warning: source_entity_name column not found")
        
        print("Schema update complete!")
        print("\nYou can now create multiple mappings for the same target entity!")
        print("Example: FODepartment -> org_unit, FOBusinessUnit -> org_unit, etc.")
        
    except Exception as e:
        print(f"Error during schema update: {e}")
    finally:
        if 'conn' in locals() and conn:
            await conn.close()

if __name__ == "__main__":
    asyncio.run(update_schema())
