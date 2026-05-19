import logging
from collections.abc import Generator
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.dao.database import SessionLocal
from app.service.db_connection import DbConnectionNotFoundError, db_connection_service


router = APIRouter(prefix="/db-connections", tags=["db-connections"])
logger = logging.getLogger(__name__)


class DbConnectionCreate(BaseModel):
    user_id: str | None = None
    name: str
    db_type: str = "postgresql"
    host: str
    port: int | None = Field(default=None, ge=1, le=65535)
    database_name: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    readonly: bool = True
    status: str = "active"
    extra: dict[str, Any] = Field(default_factory=dict)


class DbConnectionUpdate(BaseModel):
    user_id: str | None = None
    name: str | None = None
    db_type: str | None = None
    host: str | None = None
    port: int | None = Field(default=None, ge=1, le=65535)
    database_name: str | None = None
    username: str | None = None
    password: str | None = None
    ssl_mode: str | None = None
    readonly: bool | None = None
    status: str | None = None
    extra: dict[str, Any] | None = None


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def dump_request_model(model: BaseModel) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=True)
    return model.dict(exclude_unset=True)


@router.get("")
def list_db_connections(
    user_id: str | None = None,
    db_type: str | None = None,
    status: str | None = None,
    keyword: str = "",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
):
    try:
        connections, total = db_connection_service.list_connections(
            db=db,
            user_id=user_id,
            db_type=db_type,
            status=status,
            keyword=keyword.strip(),
            page=page,
            page_size=page_size,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "page": max(page, 1),
        "page_size": min(max(page_size, 1), 100),
        "total": total,
        "data": [db_connection_service.to_response(connection) for connection in connections],
    }


@router.post("")
def create_db_connection(request: DbConnectionCreate, db: Session = Depends(get_db)):
    try:
        connection = db_connection_service.create_connection(db, dump_request_model(request))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Create database connection failed")
        raise HTTPException(status_code=500, detail="create database connection failed") from exc

    return {
        "message": "database connection created",
        "data": db_connection_service.to_response(connection),
    }


@router.get("/{connection_id}")
def get_db_connection(connection_id: str, db: Session = Depends(get_db)):
    try:
        connection = db_connection_service.get_connection(db, connection_id)
    except DbConnectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"data": db_connection_service.to_response(connection)}


@router.put("/{connection_id}")
def update_db_connection(
    connection_id: str,
    request: DbConnectionUpdate,
    db: Session = Depends(get_db),
):
    try:
        connection = db_connection_service.update_connection(
            db,
            connection_id,
            dump_request_model(request),
        )
    except DbConnectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Update database connection failed: connection_id=%s", connection_id)
        raise HTTPException(status_code=500, detail="update database connection failed") from exc

    return {
        "message": "database connection updated",
        "data": db_connection_service.to_response(connection),
    }


@router.delete("/{connection_id}")
def delete_db_connection(connection_id: str, db: Session = Depends(get_db)):
    try:
        db_connection_service.delete_connection(db, connection_id)
    except DbConnectionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {"message": "database connection deleted", "connection_id": connection_id}
