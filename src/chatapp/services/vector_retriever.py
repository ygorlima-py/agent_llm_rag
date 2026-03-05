from rich import print
from langchain_core.documents import Document
from chatapp.models.vector_stores import PGVectorStoreFactory
from langchain_core.embeddings.embeddings import Embeddings


class PGVectorMMRRetriever:
    """
    Async retriever wrapper that performs Max Marginal Relevance (MMR) search on a `PGVectorStore`.

    This class provides a small, opinionated interface around LangChain's pgvector-backed store
    to retrieve a diverse set of relevant documents using MMR. It is designed to be used in
    async pipelines only.

    MMR behavior:
    - `fetch_k` controls how many candidate documents are pulled from the vector store first.
    - `lambda_mult` controls relevance vs diversity trade-off:
    - closer to 1.0 → more relevant / less diverse
    - closer to 0.0 → more diverse / less strictly relevant

    Attributes:
        store: The `PGVectorStore` instance used to run searches.
        fetch_k: Number of initial candidates to consider for MMR re-ranking.
        lambda_mult: Relevance/diversity balance parameter for MMR.

    Methods:
        invoke(input):
            Disabled sync entrypoint. Raises to enforce async usage.
        ainvoke(input):
            Runs `amax_marginal_relevance_search` on the store and returns a list of `Document`.

    Args:
        input: The user query string.

    Returns:
        list[Document]: Documents selected by MMR from the vector store.
    """

    def __init__(self,
                 factory:PGVectorStoreFactory,
                 embedding: Embeddings, 
                 table_name:str,
                 k:int = 8, 
                 fetch_k: int = 60,
                 lambda_mult: float = 0.35,
                 ):
        
        self.factory = factory
        self.k = k
        self.fetch_k = fetch_k
        self.lambda_mult = lambda_mult
        self.embedding = embedding
        self.table_name = table_name

    async def mmr_docs(self, input: str) -> list[Document]:
        store = await self.factory.create_pg_vector_store(self.table_name, self.embedding, self.k)
        return await store.amax_marginal_relevance_search( #type:ignore
            query=input,
            fetch_k=self.fetch_k,
            lambda_mult=self.lambda_mult,
        ) 

if __name__ == "__main__":
    from chatapp.models.constants import CONNECTION_STRING, TABLE_NAME
    from chatapp.models.pg_engine import PGAsyncEngine
    from chatapp.infra.load_llm import Models
    import asyncio
    

    async def run_cli() -> None:
            async_pg_engine = PGAsyncEngine(connection_str=CONNECTION_STRING)
            pg_engine = async_pg_engine.create()
            embedding = Models().embedding_model()
            factory = PGVectorStoreFactory(pg_engine=pg_engine)
            
            retriever = PGVectorMMRRetriever(factory=factory,
                                             embedding=embedding,
                                             table_name=TABLE_NAME,
                                             )
            
            docs_ret = await retriever.mmr_docs("Concentração do cletodim")
            print(docs_ret)

    asyncio.run(run_cli())