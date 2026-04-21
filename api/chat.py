import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from service.chat_llm import chat_bot


router = APIRouter(prefix="/chat", tags=["chat"])
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ClearHistoryRequest(BaseModel):
    session_id: str


@router.post("/stream")
def stream_chat(request: ChatRequest):
    if not chat_bot.api_key:
        logger.error("Chat request rejected because API_KEY is not configured")
        raise HTTPException(status_code=500, detail="API_KEY is not configured")

    logger.info("Start chat stream: session_id=%s", request.session_id)
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
    logger.info("Chat history cleared: session_id=%s", request.session_id)
    return {"message": "chat history cleared", "session_id": request.session_id}
