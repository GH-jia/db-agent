from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from service.chat_llm import chat_bot


router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ClearHistoryRequest(BaseModel):
    session_id: str


@router.post("/stream")
def stream_chat(request: ChatRequest):
    if not chat_bot.client.api_key:
        raise HTTPException(status_code=500, detail="API_KEY is not configured")

    return StreamingResponse(
        chat_bot.stream_chat(
            session_id=request.session_id,
            user_input=request.message,
        ),
        media_type="text/plain; charset=utf-8",
    )


@router.post("/clear")
def clear_chat_history(request: ClearHistoryRequest):
    chat_bot.clear_history(request.session_id)
    return {"message": "chat history cleared", "session_id": request.session_id}
