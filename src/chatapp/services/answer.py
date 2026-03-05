from langchain_core.documents import Document
from chatapp.utils.prompts import PROMPT


def build_context(documents: list[Document], max_chars: int = 12000) -> str:
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

async def answer_question(llm, question:str, docs:list[Document]):
    context = build_context(docs)

    chain = PROMPT | llm #type:ignore
    return await chain.ainvoke({'input': question, 'context': context}) #type:ignore
    

if __name__ == "__main__":
    from chatapp.models.pg_engine import PGAsyncEngine
    from chatapp.models.constants import TABLE_NAME, CONNECTION_STRING
    from chatapp.models.vector_stores import PGVectorStoreFactory
    from chatapp.infra.load_llm import Models
    from chatapp.services.lexical_retriever import PGVectorLexicalRetriever
    from chatapp.services.vector_retriever import PGVectorMMRRetriever
    from chatapp.services.rerank import Reranker
    from rich import print
    import asyncio
    
    pg_async_engine = PGAsyncEngine(connection_str=CONNECTION_STRING)
    
    pg_engine = pg_async_engine.create()
    model = Models()
    embedding = model.embedding_model() 
    factory = PGVectorStoreFactory(pg_engine=pg_engine)
    question = "Sabe me dizer se o prduto mitrion, pega mancha alvo?"
    
    lexical_retriever = PGVectorLexicalRetriever(
                                        sa_engine=pg_async_engine.sa_engine,
                                        factory=factory,
                                        table_name=TABLE_NAME,
                                        embedding=embedding,
                                        fetch_k=5,
                                        )
    
    mmr_retriever = PGVectorMMRRetriever(
                                    factory=factory,
                                    embedding=embedding,
                                    table_name=TABLE_NAME,
                                    lambda_mult=0.75,
                                    k=10,
                                    )
    
    async def run_cli(question:str):
        search_lexical_docs = await lexical_retriever.lexical_docs(question)
        search_mmr_retriever = await mmr_retriever.mmr_docs(question)
        print('MMR DOCS', search_mmr_retriever)
        print(f'Documentos por busca lexical: {len(search_lexical_docs)}')
        print(f'Documentos por busca MMR {len(search_mmr_retriever)}')
        
        reranker = Reranker(model_name_reranker='ms-marco-MiniLM-L-12-v2')
        docs = reranker.rerank(search_lexical_docs, search_mmr_retriever, query=question, top_n=8)
        
        
        response = await answer_question(
            llm=model.llm_model(),
            question=question,
            docs=docs,
        )
        
        return response.content
            
    print(asyncio.run(run_cli(question)))

