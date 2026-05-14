import logging
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from dao.database import SessionLocal
from service.chat_llm import chat_bot
from service.data_source import DataSourceConfig, data_source_manager
from service.data_source.manager import DataSourceError
from service.db_agent import db_agent_service
from service.db_connection import DbConnectionNotFoundError, db_connection_service


router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    connection_id: str
    message: str


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/query")
def query_database(request: QueryRequest, app_db: Session = Depends(get_db)):
    if not chat_bot.api_key:
        logger.error("Agent query rejected because API_KEY is not configured")
        raise HTTPException(status_code=500, detail="API_KEY is not configured")

    try:
        logger.info("Start database agent query: connection_id=%s", request.connection_id)
        connection = db_connection_service.get_connection(app_db, request.connection_id)
        data_source_config = DataSourceConfig.from_model(connection)
        schema_text = data_source_manager.get_metadata(data_source_config)
        sql = db_agent_service.generate_sql(
            request.message,
            data_source_config.db_type,
            schema_text,
        )

        db_agent_service.validate_sql(sql)
        data = data_source_manager.execute_query(data_source_config, sql)
    except DbConnectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DataSourceError as exc:
        logger.warning(
            "Database agent data source error: connection_id=%s error=%s",
            request.connection_id,
            exc,
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        logger.warning("Database agent validation failed: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Database agent query failed")
        raise HTTPException(status_code=500, detail=f"query failed: {exc}") from exc

    logger.info("Database agent query succeeded: row_count=%s", len(data))
    return {
        "connection_id": request.connection_id,
        "message": request.message,
        "sql": sql,
        "row_count": len(data),
        "data": data,
    }
