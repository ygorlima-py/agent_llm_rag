
from rich import print
from langchain_core.documents import Document
from langchain_postgres import PGVectorStore
from chatapp.services.build_documents import build_agrofit_iterable_document
from chatapp.schemas.agrofit_types import convert_json_to_formulated_product
from chatapp.infra.embrapa_api import agrofit_products
from chatapp.services.text_splitter import text_spltter_documents
from chatapp.models.pg_engine import create_async_pg_engine
from chatapp.models.vector_stores import PGVectorStoreFactory
from chatapp.models.constants import CONNECTION_STRING, TABLE_NAME
from chatapp.infra.load_llm import Models

class IndexVectorStore:
    def __init__(self, vector_store:PGVectorStore ):
        self.vector_store = vector_store
        
    async def indexing_vector_database(self, splits:list[Document]): 
        try:
            await self.vector_store.aadd_documents(documents=splits) # type:ignore
            return 'SPLITS SALVOS COM SUCESSO'
        except Exception as e:
            print(f'Error Save in data Base {e}')

# Use Just API 
async def index_multiple_documents(
    initial_page: int,
    final_page: int,    
    create_table: bool = False,
    ) -> None:
    pg_engine = create_async_pg_engine(CONNECTION_STRING)
    factory = PGVectorStoreFactory(pg_engine=pg_engine)
    model = Models()
    embedding = model.embedding_model()
    
    if create_table:
        await factory.create_table(
                        vector_size=1024,
                        table_name=TABLE_NAME,
                        number_register='text',
                        trademark='text',
                        bula='text',
                        api_url_data='text',
                        )
    vector_store = await factory.create_pg_vector_store(table_name=TABLE_NAME, embedding=embedding )
    
    current_page = initial_page
    while current_page <= final_page:      
        if current_page == 6: current_page+=2
        payload = {'page': current_page}
        products = agrofit_products(payload=payload)
        products_validated = convert_json_to_formulated_product(products=products)
        documents = build_agrofit_iterable_document(products_validated)
        splits = text_spltter_documents(documents)
        await vector_store.aadd_documents(documents=splits) #type: ignore
        
        print(f'Documento Adicionado/ page {current_page}')
        current_page+=1
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(index_multiple_documents(initial_page=41, final_page=43))
        
    


    