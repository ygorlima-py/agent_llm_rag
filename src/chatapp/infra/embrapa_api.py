import requests
from rich import print
from typing import Any
from chatapp.schemas.agrofit import FormulatedPrduct
from dotenv import load_dotenv
import os


load_dotenv()
def agrofit_products(payload: dict[str, int]) -> Any:
    
    
    '''
    This function do request to api agrofit and return a json with informations
    about formulated products
    '''
    EMBRAPA_API_KEY = os.getenv("EMBRAPA_API_KEY", "not found env")
    r = requests.get(
                    "https://api.cnptia.embrapa.br/agrofit/v1/produtos-formulados", 
                    headers={'Authorization': f'Bearer {EMBRAPA_API_KEY}'},
                    params=payload,
                    )
    
    return r.json()


if __name__ == "__main__":
    payload = {"page": 2}
    products = agrofit_products(payload=payload)

    products_validated = [FormulatedPrduct.model_validate(product) for product in products]

    print(products_validated)    
    
