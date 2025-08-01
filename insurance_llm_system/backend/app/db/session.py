import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator
from ..core.config import settings

logger = logging.getLogger(__name__)

# Database connection setup
def _create_engine():
    """Create and configure SQLAlchemy engine with proper connection args"""
    connect_args = {}
    if settings.DB_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        logger.info("Configuring SQLite database connection")
    elif settings.DB_URL.startswith("postgresql"):
        connect_args = {
            "keepalives": 1,
            "keepalives_idle": 30,
            "keepalives_interval": 10,
            "keepalives_count": 5
        }
        logger.info("Configuring PostgreSQL database connection")

    try:
        engine = create_engine(
            settings.DB_URL,
            connect_args=connect_args,
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG
        )
        logger.info(f"Database engine created for {settings.DB_URL}")
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {str(e)}")
        raise

engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(SessionLocal)
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

@contextmanager
def get_db() -> Generator[scoped_session, None, None]:
    """Database session dependency with proper cleanup"""
    db = ScopedSession()
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error occurred: {str(e)}")
        raise
    finally:
        db.close()
        ScopedSession.remove()

def get_db_session():
    """Alternative session getter for non-FastAPI contexts"""
    return get_db()

# Test database configuration (if enabled)
if settings.TEST_DB_URL:
    test_engine = create_engine(
        settings.TEST_DB_URL,
        connect_args={"check_same_thread": False} if settings.TEST_DB_URL.startswith("sqlite") else {}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    @contextmanager
    def get_test_db() -> Generator[scoped_session, None, None]:
        """Test database session with automatic cleanup"""
        db = TestingSessionLocal()
        try:
            yield db
            db.commit()
        except SQLAlchemyError:
            db.rollback()
            raise
        finally:
            db.close()
else:
    TestingSessionLocal = None
    get_test_db = None