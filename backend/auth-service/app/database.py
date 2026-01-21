"""
Database connection for Auth Service
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
import ssl
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

Base = declarative_base()

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

# Database URL (same as other services)
DATABASE_URL = "postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
db_url = convert_db_url_for_asyncpg(DATABASE_URL)

# Create SSL context for Neon
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    db_url,
    echo=False,
    future=True,
    connect_args={
        "ssl": ssl_context
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
    """Initialize database connection"""
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
