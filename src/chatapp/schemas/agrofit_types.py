from pydantic import BaseModel, Field, ConfigDict, PydanticUserError
from typing import List, Optional, Union, Any

class DetailedActiveIngredient(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    active_ingredient: str = Field(alias='ingrediente_ativo') 
    chemical_group: Optional[str] = Field(default=None, alias='grupo_quimico')
    concentration: Optional[str] = Field(default=None, alias='concentracao')
    unit_of_measurement: Optional[str] = Field(default=None, alias='unidade_medida')
    percentage: Optional[str] = Field(default=None, alias='percentual')
    
class IndicationForUse(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    culture: str = Field(alias='cultura') 
    pest_scientific_name: str = Field(alias='praga_nome_cientifico') 
    pest_usual_name: Union[List[str], str, None] = Field(alias='praga_nome_comum')
    
class Document(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    description: str = Field(alias='descricao') 
    document_type: Optional[str] = Field(default=None, alias='tipo_documento')
    date_inclusion: Optional[str] = Field(default=None, alias='data_inclusao')
    url: Optional[str] = Field(default=None, alias='url')
    origin: Optional[str] = Field(default=None, alias='origem')
    
    
class FormulatedPrduct(BaseModel):
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)
    
    register_number: str = Field(alias='numero_registro')
    trademark: List[str] = Field(default_factory=list, alias='marca_comercial')
    owner_registration: str = Field(alias='titular_registro')
    agronomic_category_class: List[str] = Field(default_factory=list, alias='classe_categoria_agronomica')
    formulation: str = Field(alias='formulacao')
    active_ingredient: List[str] = Field(default_factory=list, alias='ingrediente_ativo')
    detail_active_ingredient: List[DetailedActiveIngredient] = Field(default_factory=list, alias='ingrediente_ativo_detalhado') #type:ignore
    application_technique: List[str] = Field(default_factory=list, alias='tecnica_aplicacao')
    indications_for_use: List[IndicationForUse] = Field(default_factory=list, alias='indicacao_uso') #type:ignore
    documents: List[Document] = Field(default_factory=list, alias='documento_cadastrado') #type:ignore
    
    

def convert_json_to_formulated_product(products: Any) -> list[FormulatedPrduct]:
    try:
        return [FormulatedPrduct.model_validate(product) for product in products]
    
    except PydanticUserError:
        raise PydanticUserError(
                'At least one of `by_alias` or `by_name` must be set to True.',
                code='validate-by-alias-and-name-false',
            )