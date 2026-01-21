#!/usr/bin/env python3
"""
Automated Database Table Setup Script
Creates all required tables in PostgreSQL (Neon) database
"""

import asyncio
import asyncpg
import sys
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# Fix Windows console encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Database connection string from your config
DATABASE_URL = "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

async def run_sql_file(conn, file_path: Path):
    """Execute SQL file against database"""
    print(f"\n[INFO] Reading: {file_path.name}...")
    
    try:
        sql_content = file_path.read_text(encoding='utf-8')
        
        # Remove comments and clean up
        lines = []
        for line in sql_content.split('\n'):
            # Remove full-line comments
            if line.strip().startswith('--'):
                continue
            # Remove inline comments (keep the SQL part)
            if '--' in line:
                line = line.split('--')[0]
            lines.append(line)
        
        # Join and split by semicolon more carefully
        cleaned_sql = '\n'.join(lines)
        
        # Execute the entire SQL file as one transaction
        # PostgreSQL can handle multiple statements in one execute
        try:
            await conn.execute(cleaned_sql)
            print(f"   [SUCCESS] SQL file executed successfully")
            return True
        except Exception as e:
            # If that fails, try executing statement by statement
            print(f"   [INFO] Trying statement-by-statement execution...")
            
            # Better splitting: look for semicolons that are not inside quotes or function bodies
            statements = []
            current_statement = []
            in_string = False
            quote_char = None
            
            for char in cleaned_sql:
                if char in ("'", '"') and (not current_statement or current_statement[-1] != '\\'):
                    if not in_string:
                        in_string = True
                        quote_char = char
                    elif char == quote_char:
                        in_string = False
                        quote_char = None
                
                current_statement.append(char)
                
                if not in_string and char == ';':
                    stmt = ''.join(current_statement).strip()
                    if stmt and len(stmt) > 1:  # Ignore empty statements
                        statements.append(stmt)
                    current_statement = []
            
            # Execute each statement
            executed = 0
            for i, statement in enumerate(statements, 1):
                if statement.strip() and not statement.strip().startswith('--'):
                    try:
                        await conn.execute(statement)
                        executed += 1
                        if i % 5 == 0:
                            print(f"   [OK] Executed {i}/{len(statements)} statements...")
                    except Exception as e:
                        error_msg = str(e).lower()
                        # Ignore "already exists" errors (IF NOT EXISTS)
                        if "already exists" not in error_msg and "duplicate" not in error_msg:
                            print(f"   [WARN] Statement {i} warning: {str(e)[:150]}")
            
            print(f"   [SUCCESS] Completed: {executed}/{len(statements)} statements executed")
            return executed > 0
        
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def verify_tables(conn):
    """Verify that tables were created successfully"""
    print("\n[INFO] Verifying tables...")
    
    required_tables = [
        # Main org chart tables
        'org_unit', 'position', 'employee', 'job',
        'location', 'cost_center', 'legal_entity',
        # Functional chart tables
        'function_category', 'function', 'accountability', 'accountability_assignment'
    ]
    
    query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = ANY($1)
        ORDER BY table_name
    """
    
    result = await conn.fetch(query, required_tables)
    created_tables = [row['table_name'] for row in result]
    
    print(f"\n[STATUS] Table Status:")
    print(f"   Required: {len(required_tables)} tables")
    print(f"   Created:  {len(created_tables)} tables")
    print(f"\n[SUCCESS] Created Tables:")
    for table in sorted(created_tables):
        print(f"   + {table}")
    
    missing = set(required_tables) - set(created_tables)
    if missing:
        print(f"\n[WARNING] Missing Tables:")
        for table in sorted(missing):
            print(f"   - {table}")
        return False
    
    return True

async def get_table_counts(conn):
    """Get row counts for main tables"""
    print("\n[INFO] Table Row Counts:")
    
    tables = ['org_unit', 'position', 'employee', 'function_category', 'function', 'accountability']
    
    for table in tables:
        try:
            count = await conn.fetchval(f"SELECT COUNT(*) FROM {table}")
            print(f"   {table:30} {count:>6} rows")
        except Exception as e:
            print(f"   {table:30} ERROR: {str(e)[:50]}")

async def setup_database():
    """Main setup function"""
    print("=" * 60)
    print("OrgChartAI Database Setup")
    print("=" * 60)
    
    # Parse database URL
    parsed = urlparse(DATABASE_URL)
    query_params = parse_qs(parsed.query)
    
    # Extract connection parameters
    db_user = parsed.username
    db_password = parsed.password
    db_host = parsed.hostname
    db_port = parsed.port or 5432
    db_name = parsed.path.lstrip('/')
    
    # Handle SSL
    ssl_mode = query_params.get('sslmode', ['require'])[0]
    
    print(f"\n[INFO] Connecting to database...")
    print(f"   Host: {db_host}")
    print(f"   Database: {db_name}")
    print(f"   User: {db_user}")
    print(f"   SSL: {ssl_mode}")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name,
            ssl='require' if ssl_mode == 'require' else None
        )
        
        print("   [SUCCESS] Connected successfully!")
        
        # Get project root
        project_root = Path(__file__).parent
        database_dir = project_root / "database"
        
        # Run main schema
        schema_file = database_dir / "schema.sql"
        if not schema_file.exists():
            print(f"\n[ERROR] {schema_file} not found!")
            return False
        
        print(f"\n[STEP 1] Creating main org chart tables...")
        success1 = await run_sql_file(conn, schema_file)
        
        # Run functional chart schema
        functional_schema_file = database_dir / "functional_chart_schema.sql"
        if not functional_schema_file.exists():
            print(f"\n[WARNING] {functional_schema_file} not found, skipping...")
        else:
            print(f"\n[STEP 2] Creating functional chart tables...")
            success2 = await run_sql_file(conn, functional_schema_file)
        
        # Run triggers (optional, for auto-updating timestamps)
        triggers_file = database_dir / "triggers.sql"
        if triggers_file.exists():
            print(f"\n[STEP 3] Creating triggers and functions...")
            await run_sql_file(conn, triggers_file)
        
        # Verify tables
        if success1:
            verified = await verify_tables(conn)
            
            if verified:
                # Show table counts
                await get_table_counts(conn)
                
                print("\n" + "=" * 60)
                print("[SUCCESS] Database setup completed successfully!")
                print("=" * 60)
                print("\nNext Steps:")
                print("   1. Start HRIS Service: cd backend\\hris-service && uvicorn main:app --reload --port 8002")
                print("   2. Start Org Service: cd backend\\org-service && uvicorn main:app --reload --port 8000")
                print("   3. Connect SuccessFactors via frontend or API")
                print("   4. Start data sync")
                print("\nYour database is ready for SuccessFactors data!")
            else:
                print("\n[WARNING] Some tables may be missing. Please check the errors above.")
                return False
        else:
            print("\n[ERROR] Failed to create tables. Please check the errors above.")
            return False
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Connection Error: {str(e)}")
        print("\nTroubleshooting:")
        print("   - Check your database connection string")
        print("   - Verify network connectivity")
        print("   - Ensure database credentials are correct")
        return False

if __name__ == "__main__":
    print("\n")
    try:
        success = asyncio.run(setup_database())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[ERROR] Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
