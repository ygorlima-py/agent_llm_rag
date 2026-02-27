from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Iterable
from chatapp.infra.embrapa_api import agrofit_products
from langchain_core.documents import Document
from chatapp.services.serializers import build_agrofit_iterable_document
from chatapp.schemas.agrofit import convert_json_to_formulated_product
from rich import print


def text_spltter_documents(documents: Iterable[Document]) -> list[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=120,
        add_start_index=True,
        separators=["\n\n","\n", " ", ""],
    )

    return text_splitter.split_documents(documents)


if __name__ == '__main__':
    payload = {"page": 37}
    products = agrofit_products(payload=payload)
    products_validated = convert_json_to_formulated_product(products=products)
    documents = build_agrofit_iterable_document(products_validated)
    splits = text_spltter_documents(documents)
    print(splits)