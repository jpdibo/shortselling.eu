from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.config import settings

# Create database engine with UTF-8 encoding
if "localhost" in settings.database_url:
    # Local development
    engine = create_engine(
        settings.database_url,
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=settings.debug,
        connect_args={
            "client_encoding": "utf8",
            "options": "-c client_encoding=utf8"
        }
    )
else:
    # Production (Railway/Neon) - simpler configuration
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with tables"""
    from app.db.models import Base
    Base.metadata.create_all(bind=engine)
