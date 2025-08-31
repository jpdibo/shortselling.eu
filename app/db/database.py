from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.url import make_url
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def normalize_db_url(raw: str) -> str:
    """Normalize database URL with proper driver and SSL"""
    url = make_url(raw)
    # ensure psycopg2 driver and sslmode unless explicitly disabled
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg2")
    q = dict(url.query)
    q.setdefault("sslmode", "require")
    url = url.set(query=q)
    return str(url)

# Get the normalized database URL
DATABASE_URL = normalize_db_url(settings.database_url.get_secret_value())

# Create database engine with robust production settings
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,  # 30 minutes
    pool_timeout=30,
    echo=settings.debug,
    future=True
)

# Log connection info (without password)
db_url = make_url(DATABASE_URL)
logger.info(f"🔗 Database host: {db_url.host}; sslmode: {db_url.query.get('sslmode', 'default')}")

# Global database readiness flag
db_ready = False

def try_connect():
    """Test database connection"""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

def ensure_db_ready():
    """Ensure database is ready with retry logic"""
    global db_ready
    
    for attempt in range(5):
        try:
            logger.info(f"🔄 Database connection attempt {attempt + 1}/5")
            try_connect()
            db_ready = True
            logger.info("✅ Database connection successful")
            return
        except Exception as e:
            logger.warning(f"❌ Database connection attempt {attempt + 1} failed: {e}")
            if attempt < 4:  # Don't sleep on last attempt
                time.sleep(2 ** attempt)
    
    logger.error("❌ Database connection failed after 5 attempts")
    db_ready = False

# Create session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


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
    
    if not db_ready:
        logger.warning("⚠️ Database not ready, skipping table creation")
        return
        
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("📋 Database tables initialized")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise
