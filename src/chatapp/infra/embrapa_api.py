import os, time, json, requests
from rich import print
from typing import Any
from chatapp.schemas.agrofit_types import FormulatedPrduct
from dotenv import load_dotenv


load_dotenv()

def agrofit_products(payload: dict[str, int]) -> Any:
    EMBRAPA_API_KEY = os.getenv("EMBRAPA_API_KEY", "not found env")
    url = "https://api.cnptia.embrapa.br/agrofit/v1/search/produtos-formulados"
    headers = {
        "Authorization": f"Bearer {EMBRAPA_API_KEY}",
        "Accept-Encoding": "identity",
        "Accept": "application/json",
    }

    last_err: Exception | None = None

    for i in range(6):  # retries
        r = requests.get(url, headers=headers, params=payload, timeout=(10, 300))
        print(r.status_code)

        try:
            r.raise_for_status()

            txt = r.text.strip()
            if not (txt.endswith("]") or txt.endswith("}")):
                raise json.JSONDecodeError("truncated JSON", txt, max(len(txt) - 1, 0))

            return r.json()

        except (requests.RequestException, json.JSONDecodeError) as e:
            last_err = e
            time.sleep(min(2 ** i, 15))  # backoff

    raise RuntimeError(f"Falhou após retries. payload={payload}") from last_err


if __name__ == "__main__":
    payload = {"page": 22}
    products = agrofit_products(payload=payload)

    products_validated = [FormulatedPrduct.model_validate(product) for product in products]

    print(products_validated)    
    
