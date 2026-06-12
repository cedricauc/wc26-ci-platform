"""
Database initialization and connection management
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import Pool
from contextlib import contextmanager
import logging

from ..config import settings
from .database import Base

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Enable connection health checks
    #echo=settings.DEBUG  # Log SQL queries in debug mode
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Connection pool event listeners
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set connection parameters on connect"""
    logger.debug("New database connection established")


@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout"""
    logger.debug("Connection checked out from pool")


def init_database():
    """
    Initialize database by creating all tables
    This should be called on application startup
    """
    try:
        logger.info("Initializing database...")
        logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        logger.info(f"Tables: {', '.join(Base.metadata.tables.keys())}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise


def drop_all_tables():
    """
    Drop all tables - USE WITH CAUTION!
    Only for development/testing
    """
    if not settings.DEBUG:
        raise RuntimeError("Cannot drop tables in production mode")
    
    logger.warning("Dropping all database tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("All tables dropped")


def get_db() -> Session:
    """
    Dependency function to get database session
    Use with FastAPI Depends()
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session
    Use for non-FastAPI code
    
    Example:
        with get_db_context() as db:
            items = db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection():
    """
    Check if database connection is working
    Returns True if connection is successful, False otherwise
    """
    try:
        with get_db_context() as db:
            # Execute a simple query using text()
            db.execute(text("SELECT 1"))
        logger.info("Database connection check: SUCCESS")
        return True
    except Exception as e:
        logger.error(f"Database connection check: FAILED - {e}")
        return False


def get_table_counts():
    """
    Get row counts for all tables
    Useful for monitoring and debugging
    """
    counts = {}
    try:
        with get_db_context() as db:
            for table_name in Base.metadata.tables.keys():
                result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                counts[table_name] = result.scalar()
        return counts
    except Exception as e:
        logger.error(f"Error getting table counts: {e}")
        return {}