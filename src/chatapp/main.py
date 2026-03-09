from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from chatapp.services.rag_pipeline import RAGPipeline
from chatapp.schemas.chat_types import Chat, Response
from dotenv import load_dotenv
import os
import httpx
        
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


load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_API_KEY', 'Not found')

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "message" not in data:
        return {"ok": True}
    
    chat_id = data['message']['chat']['id']
    text = data['message'].get("text", "")
    question = str(text)
    
    pipeline = RAGPipeline()
    response = await pipeline.answer_question(question=question)
    
    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": response.content,
            }
        )
    return {"ok": True}


@app.get('/health')
async def health() -> dict[str, str]:
    return {
        'status': 'ok'
    }

