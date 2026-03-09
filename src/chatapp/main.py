from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from chatapp.services.rag_pipeline import RAGPipeline
from chatapp.schemas.chat_types import Chat, Response
        
app = FastAPI()

origins = [
    "http://localhost:5173", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],  # ou ["*"]
    allow_headers=["*"],
)

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    print(data)
    return {"ok": True}

@app.post("/main")
async def main(message: Chat) -> Response:
   pipeline = RAGPipeline()
   question = str(message)
   response = await pipeline.answer_question(question=question)
   return Response(reply=response.content)


@app.get('/health')
async def health() -> dict[str, str]:
    return {
        'status': 'ok'
    }

