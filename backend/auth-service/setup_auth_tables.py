"""
Setup script to create authentication tables
"""

import asyncio
import asyncpg
from pathlib import Path

DATABASE_URL = "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require"

async def setup_auth_tables():
    """Create authentication tables"""
    # Read SQL file
    sql_file = Path(__file__).parent.parent.parent / "database" / "auth_schema.sql"
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Execute SQL statements
        await conn.execute(sql_content)
        print("✅ Authentication tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(setup_auth_tables())
