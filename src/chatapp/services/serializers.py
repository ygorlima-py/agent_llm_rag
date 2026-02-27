from chatapp.schemas.agrofit import FormulatedPrduct
from chatapp.infra.embrapa_api import agrofit_products
from chatapp.schemas.agrofit import convert_json_to_formulated_product
from typing import Iterable
from langchain_core.documents import Document
from rich import print

def build_agrofit_product_document(product: FormulatedPrduct) -> Document:
    """
    Serialize a `FormulatedPrduct` instance into a LangChain `Document`.

    This helper converts a structured product object (typically retrieved from Agrofit/MAPA
    sources) into a text representation suitable for vector indexing and later retrieval
    in RAG pipelines (e.g., LangChain/LangGraph). It builds two outputs:

    **1) page_content**
    A human-readable, newline-delimited text block containing:
      - General product information (trade name(s), registration owner, MAPA registration number,
        agronomic class/category, formulation, active ingredient(s)).
      - Active ingredient details (chemical group, concentration, unit of measurement, percentage).
      - Application techniques.
      - Use indications grouped per crop and target pest (scientific name + common names).

    **2) metadata**
    A compact dictionary intended for filtering, tracing, and structured retrieval:
      - `source`: constant identifier for the origin system (e.g., `"agrofit"`).
      - `number_register`: MAPA registration number.
      - `trademark`: list of trade names.
      - `owner_registration`: registration owner name.
      - `agronomic_category_class`: list of agronomic classes/categories.
      - `formulation`: formulation code/description.
      - `active_ingredient`: list of active ingredient strings.
      - `pest_scientific_name`: list of strings formatted as `"<pest_scientific_name>-<culture>"`,
        derived from `product.indications_for_use`.
      - `url_sources`: list of document URLs extracted from `product.documents`.

    The function is defensive against missing/optional lists by iterating over `or []` and
    using `"-"` as a placeholder when string fields are absent. Common pest names are joined
    using `"; "` when provided as a list.

    Args:
        product: A `FormulatedPrduct` instance with optional nested fields:
            - `detail_active_ingredient`
            - `indications_for_use`
            - `documents`
            - and basic product descriptors (e.g., `trademark`, `register_number`, etc.).

    Returns:
        Document: A LangChain `Document` with:
            - `page_content` (str): formatted product description for embedding.
            - `metadata` (dict): structured fields for filtering and provenance.

    Notes:
        - Ensure `product.active_ingredient`, `product.application_technique`,
          `product.indications_for_use`, and `product.documents` are consistently typed
          (lists vs. None) to avoid runtime errors.
        - The produced content is optimized for semantic search; adjust formatting if you
          need stricter machine-readable layouts (JSON-like) for downstream parsing.
    """
    detail_ingredient: list[str] = [] 
    for detail in product.detail_active_ingredient or []:
        detail_ingredient.append(
            f"Produto: {', '.join(product.trademark)} ,"
            f"Empresa: {product.owner_registration or '-'}, "
            f"Registro: {product.register_number} ,"
            f"Ingrediente Átivo -> {detail.active_ingredient or '-'}, " 
            f"Grupo Químico -> {detail.chemical_group or '-'}, " 
            f"Concentração -> {detail.concentration or '-'}, " 
            f"Unidade de medida -> {detail.unit_of_measurement or '-'}, " 
            f"Porcentagem -> {detail.percentage or '-'}, "
            f"Técnica de aplicação: {', '.join(product.application_technique) or []}"
        )
    
    indication_for_aplication: list[str] = []
    for indication in product.indications_for_use or []:
        usual_pest_name = "; ".join(indication.pest_usual_name or [])
        indication_for_aplication.append(
            f"Produto: {', '.join(product.trademark)} ,"
            f"Empresa: {product.owner_registration or '-'}, "
            f"Registro: {product.register_number} ,"
            f"Categoria: {', '.join(product.agronomic_category_class or [])}, "
            f"Formulação: {product.formulation or '-'}, "
            f"Cultura alvo -> {indication.culture}, "
            f"Praga alvo nome científico -> {indication.pest_scientific_name}, "
            f"Praga alvo nome comum -> {usual_pest_name if isinstance(indication.pest_usual_name, list) else 'Not Found'} "          
        )
            
    page_content = "\n".join([
        f"{'\n'.join(detail_ingredient)} ",
        f"{'\n'.join(indication_for_aplication)} ",
    ])

    metadata ={
        'source': "agrofit",
        'number_register': product.register_number,
        'trademark': product.trademark or [],
        'owner_registration': product.owner_registration,
        'agronomic_category_class': product.agronomic_category_class or [],
        'formulation': product.formulation,
        'active_ingredient': product.active_ingredient or [],
        'documents': {
            'bula':f"https://api.agrobula.com.br/public/bulas/{product.register_number}.pdf",
            'api':f"https://api.agrobula.com.br/api/v1/produtos/{product.register_number}"
        }
    }
    
    return Document(
        metadata=metadata,
        page_content=page_content,
    )
    
def build_agrofit_iterable_document(formulated_products: list[FormulatedPrduct]) -> Iterable[Document]:
    """
    Build an iterable of LangChain `Document` objects from a list of Agrofit formulated products.

    This function converts each `FormulatedPrduct` in `formulated_products` into a LangChain
    `Document` by delegating the transformation to `build_agrofit_product_document`. The
    resulting documents are suitable for vector indexing and retrieval in RAG pipelines.

    Args:
        formulated_products: A list of `FormulatedPrduct` instances to be serialized into
            `Document` objects.

    Returns:
        An iterable (currently a list) of LangChain `Document` objects, one per product.
    """
    
    documents = [build_agrofit_product_document(product) for product in formulated_products]
    
    return documents
    
    
    
if __name__ == "__main__":
    fake_data = {
            "numero_registro": "44225",
            "marca_comercial": ["Eraser"],
            "titular_registro": "Biorisk - Assessoria e Comércio de Produtos Agrícolas Ltda.",
            "classe_categoria_agronomica": ["Herbicida"],
            "formulacao": "CS - Suspensão de Encapsulado",
            "ingrediente_ativo": ["clomazona (isoxazolidinona) (360 g/L)"],
            "ingrediente_ativo_detalhado": [
                 {
                    "ingrediente_ativo": "clomazona",
                    "grupo_quimico": "isoxazolidinona", 
                    "concentracao": "360",
                    "unidade_medida": "g/L",
                    "percentual": "36%",
                },
                {
                    "ingrediente_ativo": "trifloxistrobina'",
                    "grupo_quimico":  'estrobilurina',
                    "concentracao": '150',
                    "unidade_medida": 'Gramas por Litros',
                    "percentual": '15',
                }
                 ],
            "tecnica_aplicacao": ["Pulverização"],
            "indicacao_uso": [
                {
                    "cultura": 'Algodão',
                    "praga_nome_cientifico": 'Alternaria solani',
                    "praga_nome_comum": ['Fura-capa'],
                }
                ],
            "documento_cadastrado": [
                {
                    'descricao': 'EREDITÀ; SOLENZA; ORIZZONTE_Bula Agrofit_v03',
                    'tipo_documento': 'Bula',
                    'date_inclusion': '10/07/2025 14:47:25',
                    'url': 'https://agrofit.agricultura.gov.br/agrofit_cons/agrofit.ap_download_blob_agrofit?p_id_file=487238&p_nm_file=F922383791/SEI_MAPA%20-%2035479330%20-%20Agrot%C3%B3xicos%20-%20Certificado%20de%20Agrot%C3%B3xicos%20e%20Afins.pdf',
                    'origin': 'Bula, Rótulo e Certificado'
                }
            ]
        }

    payload = {"page": 3}
    products = agrofit_products(payload=payload)
    products_validated = convert_json_to_formulated_product(products=products)

    for product in products_validated:
        document = build_agrofit_product_document(product)
        print(document)
    