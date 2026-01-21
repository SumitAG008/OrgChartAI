"""
Database connection and session management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create async engine
# asyncpg doesn't support sslmode parameter, need to parse and convert
def convert_db_url_for_asyncpg(url: str) -> str:
    """Convert PostgreSQL URL from psycopg2 format to asyncpg format"""
    # Remove sslmode and channel_binding from query string
    from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
    
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

# Create async engine with SSL enabled for Neon
# asyncpg requires SSL - create SSL context for Neon
import ssl

# Create SSL context for Neon (SSL required but can skip verification)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_async_engine(
    convert_db_url_for_asyncpg(settings.DATABASE_URL),
    echo=False,
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "ssl": ssl_context,  # Neon requires SSL
        "server_settings": {
            "search_path": "public"  # Explicitly set search path
        }
    }
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

# Dependency for getting DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database
async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        # Tables are created via migrations
        pass
