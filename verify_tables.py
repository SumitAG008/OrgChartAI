"""Quick script to verify tables exist"""
import asyncio
import asyncpg
import ssl

async def verify():
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    conn = await asyncpg.connect(
        host='ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech',
        port=5432,
        user='neondb_owner',
        password='npg_Mruj0FCPdbT9',
        database='neondb',
        ssl=ssl_context
    )
    
    result = await conn.fetchval("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('position', 'employee', 'org_unit', 'function_category', 'function', 'accountability')
    """)
    
    print(f"[SUCCESS] Found {result} tables in database")
    
    # List all tables
    tables = await conn.fetch("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    
    print("\n[INFO] All tables in 'public' schema:")
    for row in tables:
        print(f"   + {row['table_name']}")
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(verify())
