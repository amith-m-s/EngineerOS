"""Database connection and session management with connection pooling."""

import logging

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, StaticPool

from .config import get_settings

logger = logging.getLogger(__name__)


def create_db_engine():
    """
    Create SQLAlchemy engine with connection pooling.
    
    Uses QueuePool for production PostgreSQL (threaded servers).
    Uses StaticPool for SQLite (development fallback).
    Uses NullPool for testing.
    """
    settings = get_settings()
    database_url = settings.postgres_dsn

    # SQLite requires special handling — no connection pool args, check_same_thread=False
    if settings.is_sqlite:
        logger.info(f"Using SQLite database: {database_url}")
        engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )
        return engine

    # Determine pool class based on environment
    if settings.environment == "testing":
        # Testing: minimal connection pooling
        poolclass = pool.NullPool
        pool_config: dict = {}
    elif settings.environment == "development":
        # Development: small pool
        poolclass = QueuePool
        pool_config = {
            "pool_size": 5,
            "max_overflow": 10,
            "pool_pre_ping": True,
            "pool_recycle": 3600,  # Recycle connections after 1 hour
        }
    else:
        # Production: larger pool with better settings
        poolclass = QueuePool
        pool_config = {
            "pool_size": 20,
            "max_overflow": 40,
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "echo_pool": False,
            "connect_args": {
                "connect_timeout": 10,
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            },
        }

    engine = create_engine(
        database_url,
        poolclass=poolclass,
        echo=settings.debug and settings.environment == "development",
        **pool_config,
    )

    # Setup connection pool logging
    if settings.debug:
        @event.listens_for(pool.Pool, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Log when connection is established."""
            logger.debug(f"Database connection established: {id(dbapi_connection)}")

        @event.listens_for(pool.Pool, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log when connection is checked out from pool."""
            logger.debug(f"Connection checked out: {id(dbapi_connection)}")

    return engine


# Create engine instance (lazy-safe — defaults to SQLite if no Postgres configured)
engine = create_db_engine()

# Create session factory
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


def get_db_session() -> Session:
    """Get database session for dependency injection."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_db():
    """Sync database session (for non-async contexts)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
