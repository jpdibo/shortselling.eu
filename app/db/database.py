from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import time
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Use the database URL directly from settings - NO MODIFICATIONS
DATABASE_URL = settings.database_url
print(f"🐛 USING DATABASE_URL: {DATABASE_URL}")

# Create simple database engine 
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.debug
)

print(f"🐛 ENGINE CREATED SUCCESSFULLY")

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
            print(f"🔄 Database connection attempt {attempt + 1}/5")
            try_connect()
            db_ready = True
            print("✅ Database connection successful")
            return
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1} failed: {str(e)}")
            print(f"❌ Error type: {type(e).__name__}")
            if attempt < 4:  # Don't sleep on last attempt
                time.sleep(2 ** attempt)
    
    print("❌ Database connection failed after 5 attempts")
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
        print("⚠️ Database not ready, skipping table creation")
        return
        
    try:
        Base.metadata.create_all(bind=engine)
        print("📋 Database tables initialized")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        raise
