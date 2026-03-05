from langchain_postgres import PGEngine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine  # cria engine async do SQLAlchemy


class PGAsyncEngine:
    def __init__(self, connection_str: str):
        self.connection_str = connection_str
        self.sa_engine: AsyncEngine = create_async_engine(self.connection_str)
            
    def create(self) -> PGEngine:
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
            pg_engine = PGEngine.from_engine(engine=self.sa_engine)
            
            return pg_engine
        
        except Exception as e:
            print(f'Failed to create PGEngine {e}')
            raise 
        

