from sqlalchemy.ext.asyncio import create_async_engine
from langchain_postgres import PGEngine

def create_async_pg_engine(connection_str: str) -> PGEngine:
    """
    Create and return a `PGEngine` backed by an async SQLAlchemy engine.

    This helper builds a SQLAlchemy async engine using the provided connection string and
    wraps it in LangChain's `PGEngine`, which is used to manage Postgres/pgvector
    operations (e.g., initializing tables, connecting vector stores).

    Args:
        connection_str: SQLAlchemy async connection string (e.g.
            `"postgresql+psycopg://user:pass@host:port/dbname"` or similar).

    Returns:
        PGEngine: A LangChain Postgres engine wrapper created from the async SQLAlchemy engine.

    Raises:
        Exception: Re-raises any connection/engine creation error after logging.
    """
    try:
        engine = create_async_engine(
            connection_str,
        )
        return PGEngine.from_engine(engine=engine)
    
    except Exception as e:
        print(f'Failed to create PGEngine {e}')
        raise 
    

