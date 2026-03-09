from langchain_core.documents import Document
from chatapp.utils.prompts import PROMPT
from chatapp.models.pg_engine import PGAsyncEngine
from chatapp.models.vector_stores import PGVectorStoreFactory
from chatapp.infra.load_llm import AIModels
from chatapp.services.lexical_retriever import PGVectorLexicalRetriever
from chatapp.services.vector_retriever import PGVectorMMRRetriever
from chatapp.services.rerank import Reranker
from chatapp.models.constants import TABLE_NAME, CONNECTION_STRING
from rich import print
import asyncio

class RAGPipeline:
    def __init__(self):
        self.embedding = AIModels().embedding_model()
        self.llm = AIModels().llm_model()
        self.pg_async_engine = PGAsyncEngine(CONNECTION_STRING)
        self.pg_engine = self.pg_async_engine.create()
        self.factory = PGVectorStoreFactory(pg_engine=self.pg_engine)
        self.lexical_retriever = PGVectorLexicalRetriever(
                                                        sa_engine=self.pg_async_engine.sa_engine,
                                                        table_name=TABLE_NAME,
                                                        factory=self.factory,
                                                        embedding=self.embedding,
                                                        fetch_k=5,
                                                        )
        self.mmr_retriever = PGVectorMMRRetriever(
                                        factory=self.factory,
                                        embedding=self.embedding,
                                        table_name = TABLE_NAME,
                                        lambda_mult= 0.75,
                                        k=10,
                                            )   
        self.reranker = Reranker(model_name_reranker='ms-marco-MiniLM-L-12-v2')         
    
    async def _get_documents(self, question) -> list[Document]:
        search_lexical_docs = await self.lexical_retriever.lexical_docs(question)
        search_mmr_retriever = await self.mmr_retriever.mmr_docs(question)
        return  self.reranker.rerank(search_lexical_docs, search_mmr_retriever, query=question, top_n=8)
    
        
    async def _build_context(self, question:str, max_chars: int = 12000) -> str:
        
        documents = await self._get_documents(question)
        parts: list[str] = []
        size = 0
        for d in documents:
            meta = d.metadata or {}
            urls = meta.get('documents')
            leaflet = urls.get('bula', '')
            chunk = f"\nUrl da Bula: {leaflet}\n Conteudo: {d.page_content}"
            if size + len(chunk) > max_chars:
                break
            parts.append(chunk)
            size += len(chunk)
        return f'\n----------------\n'.join(parts)

    async def answer_question(self, question:str):
        context = await self._build_context(question)
        chain = PROMPT | self.llm #type:ignore
        return await chain.ainvoke({'input': question, 'context': context}) #type:ignore
    

if __name__ == "__main__":
    rag = RAGPipeline()
    response = asyncio.run(rag.answer_question('Me traga a bula do maxim quattro'))
    print(response.content)