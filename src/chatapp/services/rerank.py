from flashrank import Ranker, RerankRequest  # type:ignore
from langchain_core.documents import Document  
from typing import Dict, Any
from rich import print

class Reranker:
    def __init__(self, model_name_reranker: str):
        self.model_name = model_name_reranker
        
    def _union_documents_list(self, *docs_list) -> list[Document]:
        union_documents:list[Document] = []
        for _list in docs_list:
            union_documents.extend(_list)
        return union_documents
            
    def _dedup(self, *docs_list) -> list[Document]:
        docs = self._union_documents_list(*docs_list)
        
        seen = set()
        unique_docs = []
        for doc in docs:
            doc_id = doc.id
            
            if doc_id in seen:
                continue
            seen.add(doc_id)
            unique_docs.append(doc)
        
        return unique_docs 

    def rerank(self, *documents, query: str, top_n: int = 7) -> list[Document]:
        
        docs = self._dedup(*documents)
        RERANKER = Ranker(model_name=self.model_name)
        if not docs:
            return []
        
        passages: list[Dict[str, Any]] = []
        for i, d in enumerate(docs):
            passages.append({
                'id': str(i),
                'text': d.page_content,                
                })
            
        req = RerankRequest(
            query=query,
            passages=passages,
        )
            
        ranked = RERANKER.rerank(req)
        
        top = ranked[:top_n]
        
        return [docs[int(item['id'])] for item in top]

if __name__ == "__main__":
    from chatapp.models.pg_engine import PGAsyncEngine
    from chatapp.models.constants import TABLE_NAME, CONNECTION_STRING
    from chatapp.models.vector_stores import PGVectorStoreFactory
    from chatapp.infra.load_llm import AIModels
    from chatapp.services.lexical_retriever import PGVectorLexicalRetriever
    from chatapp.services.vector_retriever import PGVectorMMRRetriever
    import asyncio
    
    pg_async_engine = PGAsyncEngine(connection_str=CONNECTION_STRING)
    
    pg_engine = pg_async_engine.create()
    model = AIModels()
    embedding = model.embedding_model() 
    factory = PGVectorStoreFactory(pg_engine=pg_engine)
    question = "Fox Supra"
    
    lexical_retriever = PGVectorLexicalRetriever(
                                        sa_engine=pg_async_engine.sa_engine,
                                        factory=factory,
                                        table_name=TABLE_NAME,
                                        embedding=embedding,
                                        fetch_k=30,
                                        )
    
    mmr_retriever = PGVectorMMRRetriever(
                                    factory=factory,
                                    embedding=embedding,
                                    table_name=TABLE_NAME,
                                    lambda_mult=0.75,
                                    k=30,
                                    )
    
    async def run_cli(question):
        search_lexical_docs = await lexical_retriever.lexical_docs(question)
        search_mmr_retriever = await mmr_retriever.mmr_docs(question)
        
        print(f'Documentos por busca lexical: {len(search_lexical_docs)}')
        print(f'Documentos por busca MMR {len(search_mmr_retriever)}')
        
        reranker = Reranker(model_name_reranker='ms-marco-MiniLM-L-12-v2')
        
        print(reranker.rerank(search_lexical_docs, search_mmr_retriever, query=question, top_n=8))
            
    asyncio.run(run_cli(question))

