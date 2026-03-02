import asyncio
from rich import print

from langchain_postgres import PGVectorStore
from langchain_core.documents import Document

from chatapp.models.constants import CONNECTION_STRING, TABLE_NAME
from chatapp.models.pg_engine import create_async_pg_engine
from chatapp.models.vector_stores import PGVectorStoreFactory
from chatapp.infra.load_llm import Models


class PGVectorMMRRetriever:
    """Retriever limpo: busca com MMR e já devolve poucos docs pro contexto."""

    def __init__(self, store: PGVectorStore, fetch_k: int = 80, lambda_mult: float = 0.35):
        self.store = store
        self.fetch_k = fetch_k
        self.lambda_mult = lambda_mult

    def invoke(self, input: str) -> list[Document]:
        raise RuntimeError("Use 'ainvoke' (async)")

    async def ainvoke(self, input: str) -> list[Document]:
        return await self.store.amax_marginal_relevance_search( #type:ignore
            query=input,
            fetch_k=self.fetch_k,
            lambda_mult=self.lambda_mult,
        ) 


async def build_store() -> PGVectorStore:
    pg_engine = create_async_pg_engine(connection_str=CONNECTION_STRING)
    embedding = Models().embedding_model()
    factory = PGVectorStoreFactory(pg_engine=pg_engine)
    return await factory.create_pg_vector_store(table_name=TABLE_NAME, embedding=embedding)


async def run_cli() -> None:
        store = await build_store()
        
        # Teste via retriever - altere k_final para 60
        retriever = PGVectorMMRRetriever(store, fetch_k=200, lambda_mult=0.35)
        docs_ret = await retriever.ainvoke("Cropstar")
        print(docs_ret)


if __name__ == "__main__":
    asyncio.run(run_cli())