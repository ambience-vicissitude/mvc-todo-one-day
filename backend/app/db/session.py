"""Database session and engine management.

Provides cached SQLAlchemy engine and session factory, and a generator for database sessions.

Note: The following are common bottlenecks when using SQLAlchemy with a database connection pool.
-  If there is a bottleneck at the connection level, consider the pool size and max overflow settings or adopt PgBouncer.
-  If there is a bottleneck at the session level, consider adjusting the session factory settings.
-  If there is a bottleneck at the query level, consider optimizing your SQL queries or adding appropriate indexes.
-  If there is a bottleneck at the transaction level, consider reviewing your transaction management strategy.

Note 2: Use SQLAlchemy pool settings when the application process needs more connections and
Postgres can safely handle them. Use PgBouncer when the app needs many client connections,
but Postgres should keep a smaller, controlled number of server connections.

"""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    """Get cached SQLAlchemy engine."""

    settings = get_settings()
    return create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,  # pool allows this many connections per worker
        max_overflow=settings.db_max_overflow,  # additional connections beyond the pool size
        pool_pre_ping=True,  # replace connections dropped by a Postgres restart
    )


@lru_cache
def _session_factory() -> sessionmaker[Session]:
    """Get cached SQLAlchemy session factory."""

    # Note: by caching the session factory, we avoid recreating it for each request, which improves performance.
    # autoflush=False allows us control over flush timing for database changes
    # expire_on_commit=False keeps ORM object attributes available, which can improve performance by reducing unnecessary reloads from the database.
    return sessionmaker(
        bind=get_engine(),  # bind the session to the cached engine
        autoflush=False,  # do not automatically flush changes to the database
        expire_on_commit=False,  # do not expire objects on commit
    )


def get_db() -> Iterator[Session]:
    """Provide a database session generator."""

    # Note: Creates a fresh session for this use and enters its context manager.
    # When the context exits, SQLAlchemy closes the session and releases any checked-out connection back to the pool.
    # It does not automatically commit; the repository code commits its writes explicitly.
    with _session_factory()() as session:
        # Hands the session over to the caller (which is the route handling the request)
        yield session
