from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# Create async engine for modern, non-blocking DB connections
# We use asyncpg because it is much faster and doesn't block the Python event loop
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Create an async session maker
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

# Base class for our database models
Base = declarative_base()

# Dependency to get the database session in our API routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
