from pydantic import BaseModel
from typing import Any


class Chat(BaseModel):
    message: str

class Response(BaseModel):
    reply: str | list[str | dict[str, Any]]