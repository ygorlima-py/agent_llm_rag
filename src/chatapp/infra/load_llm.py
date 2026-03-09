from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dataclasses import dataclass
from dotenv import load_dotenv
import os 

load_dotenv()

OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "not found env")

@dataclass
class ModelsParams:
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str = OPENROUTER_API_KEY

class AIModels(ModelsParams):
    
    def embedding_model(self) -> OpenAIEmbeddings:
        return OpenAIEmbeddings(
            model="intfloat/e5-large-v2",
            base_url=self.base_url,
            api_key=self.api_key,
            tiktoken_enabled=False,
        )
    
    def llm_model(self, temperature: float = 0.7) -> ChatOpenAI:
    
        return  ChatOpenAI(
                model="baidu/ernie-4.5-21b-a3b-thinking",
                base_url=self.base_url,
                api_key=self.api_key,
                temperature=temperature,
                )

if __name__ == "__main__":
    model = AIModels()
    llm_model = model.llm_model()
    response = llm_model.invoke("Olá LLM")
    print(response)