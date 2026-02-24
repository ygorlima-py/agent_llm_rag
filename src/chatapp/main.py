from fastapi import FastAPI
from pydantic import BaseModel
from chatapp.infra.load_llm import Models
from typing import Any



class Chat(BaseModel):
    ask: str

class Response(BaseModel):
    answer: str | list[str | dict[str, Any]]
        
app = FastAPI()

@app.post("/main")
async def main(chat: Chat) -> Response:
    model = Models()
    llm_model = model.llm_model()
    result = llm_model.invoke(chat.ask)
    response = Response(answer=result.content) # type: ignore
    return response


@app.get('/health')
async def health() -> dict[str, str]:
    return {
        'status': 'ok',
    }

