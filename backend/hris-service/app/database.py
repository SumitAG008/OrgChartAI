"""
Database connection and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from app.config import settings
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

Base = declarative_base()

def parse_database_url(url: str) -> str:
    """Parse database URL and remove asyncpg-incompatible parameters"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove parameters that asyncpg doesn't support
    query_params.pop('sslmode', None)
    query_params.pop('channel_binding', None)
    
    # Rebuild URL
    new_query = urlencode(query_params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    return urlunparse(new_parsed)

# Parse and create engine
# Convert to asyncpg format if needed
def convert_db_url_for_asyncpg(url: str) -> str:
    """Convert PostgreSQL URL from psycopg2 format to asyncpg format"""
    parsed = urlparse(url)
    query_params = parse_qs(parsed.query)
    
    # Remove asyncpg-incompatible parameters
    query_params.pop('sslmode', None)
    query_params.pop('channel_binding', None)
    
    # Rebuild query string
    new_query = urlencode(query_params, doseq=True)
    
    # Reconstruct URL
    new_parsed = parsed._replace(query=new_query)
    new_url = urlunparse(new_parsed)
    
    # Convert to asyncpg format
    return new_url.replace("postgresql://", "postgresql+asyncpg://")

db_url = convert_db_url_for_asyncpg(settings.DATABASE_URL)

# Create SSL context for Neon
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args={
        "ssl": ssl_context  # Neon requires SSL
    }
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    """Initialize database connection and create tables"""
    async with engine.begin() as conn:
        # Test connection
        await conn.execute(text("SELECT 1"))
        
        # Create HRIS tables if they don't exist
        # Execute statements one by one to handle errors gracefully
        
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
        
        # Execute all statements
        for statement in statements:
            try:
                await conn.execute(text(statement))
            except Exception as e:
                # Ignore "already exists" errors
                error_str = str(e).lower()
                if "already exists" not in error_str and "duplicate" not in error_str:
                    # Log but don't fail - tables might be partially created
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Table creation note: {str(e)[:100]}")
