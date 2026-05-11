import logging
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from service.chat_llm import chat_bot
from service.db_agent import db_agent_service


router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    message: str


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/query")
def query_database(request: QueryRequest, db: Session = Depends(get_db)):
    if not chat_bot.api_key:
        logger.error("Agent query rejected because API_KEY is not configured")
        raise HTTPException(status_code=500, detail="API_KEY is not configured")

    try:
        logger.info("Start database agent query")
        sql = db_agent_service.generate_sql(request.message)

        db_agent_service.validate_sql(sql)
        data = db_agent_service.execute_query(db, sql)
    except ValueError as exc:
        logger.warning("Database agent validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Database agent query failed")
        raise HTTPException(status_code=500, detail=f"query failed: {exc}") from exc

    logger.info("Database agent query succeeded: row_count=%s", len(data))
    return {
        "message": request.message,
        "sql": sql,
        "row_count": len(data),
        "data": data,
    }
