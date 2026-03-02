from typing import Union, List
from langchain_postgres import PGEngine
from langchain_postgres import PGVectorStore
from langchain_postgres.v2.engine import Column, ColumnDict
from langchain_core.embeddings.embeddings import Embeddings
from langchain_postgres.v2.hybrid_search_config import HybridSearchConfig  # ajuste o import se seu pacote expor em outro path
from sqlalchemy.exc import ProgrammingError

class PGVectorStoreFactory:
    """
    Factory utilities for setting up and connecting to a LangChain `PGVectorStore`.

    This class groups the two common steps needed to use pgvector with LangChain:
    1) Create/initialize the vectorstore table (with the correct embedding dimension and metadata columns).
    2) Create a `PGVectorStore` instance bound to that table.

    It is meant to keep Postgres/pgvector setup in one place and reuse a shared `PGEngine`.

    Attributes:
        pg_engine: A `PGEngine` instance used to initialize tables and create vector stores.

    Methods:
        create_table(vector_size, table_name, **metadata_fields):
            Initializes the underlying vectorstore table with a fixed embedding dimension and
            typed metadata columns. Pass metadata columns as keyword arguments where the key is
            the column name and the value is the Postgres data type (e.g., `text`, `int`, `numeric`).

        create_pg_vector_store(table_name, embedding):
            Returns a `PGVectorStore` connected to the given table, using the provided embedding
            service to embed documents.

    Example:
        factory = PGVectorStoreFactory(pg_engine)

        await factory.create_table(
            vector_size=1536,
            table_name="vectorstore",
            register_number="text",
            culture="text",
            pest_scientific_name="text",
            formulation="text",
        )

        store = await factory.create_pg_vector_store(table_name="vectorstore", embedding=embedding)
    """
    def __init__(self, pg_engine:PGEngine):
        self.pg_engine = pg_engine
    
    async def create_table(self, vector_size: int, table_name:str, **metadata_fields: str) -> None:
            metadata_columns: List[Union[Column,ColumnDict]]  = [Column(name=name, data_type=data_type) for name, data_type in metadata_fields.items()]   
            await self.pg_engine.ainit_vectorstore_table(
                table_name=table_name,
                vector_size=vector_size,
                metadata_columns=metadata_columns
            )
            
    async def create_pg_vector_store(self, table_name:str, embedding: Embeddings) -> PGVectorStore:
            hybrid_cfg = HybridSearchConfig()
            hybrid_cfg.primary_top_k = 8
            hybrid_cfg.secondary_top_k = 8
            
            store = await PGVectorStore.create(
                                engine=self.pg_engine,
                                table_name=table_name,
                                # schema_name=SCHEMA_NAME,
                                embedding_service=embedding,
                                hybrid_search_config=hybrid_cfg,
                        )
            try:
                await store.aapply_hybrid_search_index() #type:ignore
            except ProgrammingError as e:
                
                if "already exists" not in str(e):
                    raise    
            return store
        

        
        
    
    
