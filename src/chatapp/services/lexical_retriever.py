from typing import List
from chatapp.models.pg_engine import PGAsyncEngine
from chatapp.models.constants import TABLE_NAME, CONNECTION_STRING
from chatapp.models.vector_stores import PGVectorStoreFactory
from chatapp.infra.load_llm import Models
from langchain_core.documents import Document
from langchain_core.embeddings.embeddings import Embeddings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
import asyncio
from rich import print

class PGVectorLexicalRetriever:
    """
    This class runs a lexical search (Postgres `to_tsvector` / `plainto_tsquery`) against the
    raw text column of a pgvector-backed table to find matching rows, returns their ids, and
    then fetches the corresponding LangChain `Document` objects from the `PGVectorStore`.

    It is useful for hybrid retrieval (BM25/FTS + vector search), or as a fallback when you
    want exact keyword matching.

    Args:
        sa_engine: Async SQLAlchemy engine used to execute the raw SQL full-text query.
        table_name: Name of the Postgres table that stores the documents/vectors.
        factory: `PGVectorStoreFactory` used to create/connect a `PGVectorStore` for the same table.
        embedding: Embedding service instance required by `PGVectorStore.create(...)`.
        k: Maximum number of ids to return from the lexical search (LIMIT).
        language: PostgreSQL text search configuration (e.g., "portuguese", "english").
        text_column: Name of the column containing the raw text used for FTS
            (must match the actual table schema).
        id_column: Name of the id column to return from the table (must match the actual schema).
    """
    def __init__(self,  sa_engine: AsyncEngine,
                        table_name: str,
                        factory:PGVectorStoreFactory,
                        embedding: Embeddings,
                        fetch_k: int = 30,
                        language: str = "portuguese",
                        text_column: str = "content",  # <-- troque pro nome real da coluna de texto
                        id_column: str = "langchain_id",
                ):
        self.sa_engine = sa_engine
        self.table_name = table_name
        self.factory = factory
        self.fetch_k = fetch_k
        self.embedding = embedding
        self.language = language
        self.text_column = text_column
        self.id_column = id_column
        
    async def lexical_search_ids(self, query: str) -> List[str]:
        """
        lexical_search_ids(query):
        Runs a Postgres full-text search query and returns up to `k` matching ids as strings.
        - Returns an empty list if the query is empty/blank.
        
        """
        q = (query or "").strip()
        
        if not q:
            return []
        
        tokens = [t for t in q.split() if len(t) >= 4]
        tokens_or = " OR ".join(tokens[:6]) if tokens else q
                
        sql = f""" 
                   WITH q AS (
                    SELECT
                        websearch_to_tsquery('{self.language}', :tokens_or) AS q_anchor,
                        websearch_to_tsquery('{self.language}', :q)      AS q_full
                    )
                    SELECT {self.id_column} AS id
                    FROM {self.table_name}, q
                    WHERE to_tsvector('{self.language}', {self.text_column}) @@ q.q_anchor
                    ORDER BY
                    ts_rank(to_tsvector('{self.language}', {self.text_column}), q.q_anchor) +
                    0.2 * ts_rank(to_tsvector('{self.language}', {self.text_column}), q.q_full) DESC
                    LIMIT :k
                """
        async with self.sa_engine.begin() as conn:
            result = await conn.execute(text(sql), {"tokens_or": tokens_or, "q": q, "k": self.fetch_k})
            rows = result.mappings().all()  
        return [str(r["id"]) for r in rows]

    async def lexical_docs(self, question: str) -> list[Document]:
        """
         Convenience method that:
        1) gets ids via `lexical_search_ids`,
        2) connects to the `PGVectorStore` via the factory,
        3) fetches the matching documents using `store.aget_by_ids(ids)`.

        Args:
            question (str): Question of user

        Returns:
            list[Document]: an empty list when no ids match
        """
        
        ids = await self.lexical_search_ids(query=question)
        if not ids:
            return []
        store = await self.factory.create_pg_vector_store(table_name=self.table_name, embedding=self.embedding)
        return await store.aget_by_ids(ids)


if __name__ == "__main__":
    pg_async_engine = PGAsyncEngine(connection_str=CONNECTION_STRING)
    pg_engine = pg_async_engine.create()
    model = Models()
    embedding = model.embedding_model() 
    factory = PGVectorStoreFactory(pg_engine=pg_engine)
    question = "sabe me dizer se cletodim pega corda de viola"
    
    retriever = PGVectorLexicalRetriever(sa_engine=pg_async_engine.sa_engine,
                                         factory=factory,
                                         table_name=TABLE_NAME,
                                         embedding=embedding
                                         )
    
    
    docs = asyncio.run(retriever.lexical_docs(question=question))
    print(docs)