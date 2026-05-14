import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from dao.models import AgentDbConnectionModel


logger = logging.getLogger(__name__)

SUPPORTED_DB_TYPES = {"postgresql", "mysql"}
DEFAULT_PORTS = {
    "postgresql": 5432,
    "mysql": 3306,
}
SUPPORTED_SSL_MODES = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}
SUPPORTED_STATUSES = {"active", "disabled"}


class DbConnectionNotFoundError(Exception):
    pass


class DbConnectionService:
    def create_connection(self, db: Session, data: dict[str, Any]) -> AgentDbConnectionModel:
        self._validate_connection_data(data, partial=False)
        db_type = self._normalize_db_type(data.get("db_type"))
        connection = AgentDbConnectionModel(
            connection_id=self._new_connection_id(),
            user_id=data.get("user_id"),
            name=data["name"].strip(),
            db_type=db_type,
            host=data["host"].strip(),
            port=self._resolve_port(data.get("port"), db_type),
            database_name=data["database_name"].strip(),
            username=data["username"].strip(),
            password=data["password"],
            ssl_mode=data.get("ssl_mode", "prefer"),
            readonly=bool(data.get("readonly", True)),
            status=data.get("status", "active"),
            extra=data.get("extra") or {},
        )
        db.add(connection)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            logger.warning("Database connection create failed because connection_id duplicated")
            raise ValueError("database connection already exists") from exc

        db.refresh(connection)
        logger.info("Database connection created: connection_id=%s", connection.connection_id)
        return connection

    def list_connections(
        self,
        db: Session,
        user_id: str | None = None,
        db_type: str | None = None,
        status: str | None = None,
        keyword: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AgentDbConnectionModel], int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)

        query = db.query(AgentDbConnectionModel)
        if user_id:
            query = query.filter(AgentDbConnectionModel.user_id == user_id)
        if db_type:
            db_type = self._normalize_db_type(db_type)
            query = query.filter(AgentDbConnectionModel.db_type == db_type)
        if status:
            if status not in SUPPORTED_STATUSES:
                raise ValueError("status must be active or disabled")
            query = query.filter(AgentDbConnectionModel.status == status)
        if keyword:
            like_keyword = f"%{keyword}%"
            query = query.filter(AgentDbConnectionModel.name.ilike(like_keyword))

        total = query.count()
        connections = (
            query.order_by(AgentDbConnectionModel.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        logger.info("Database connections listed: total=%s page=%s page_size=%s", total, page, page_size)
        return connections, total

    def get_connection(self, db: Session, connection_id: str) -> AgentDbConnectionModel:
        connection = (
            db.query(AgentDbConnectionModel)
            .filter(AgentDbConnectionModel.connection_id == connection_id)
            .first()
        )
        if not connection:
            raise DbConnectionNotFoundError("database connection not found")
        return connection

    def update_connection(
        self,
        db: Session,
        connection_id: str,
        data: dict[str, Any],
    ) -> AgentDbConnectionModel:
        connection = self.get_connection(db, connection_id)
        update_data = {key: value for key, value in data.items() if value is not None}
        self._validate_connection_data(update_data, partial=True)
        if "db_type" in update_data:
            update_data["db_type"] = self._normalize_db_type(update_data["db_type"])
        if "port" in update_data:
            update_data["port"] = self._resolve_port(update_data["port"], update_data.get("db_type", connection.db_type))

        for field in [
            "user_id",
            "name",
            "db_type",
            "host",
            "port",
            "database_name",
            "username",
            "ssl_mode",
            "readonly",
            "status",
            "extra",
        ]:
            if field not in update_data:
                continue
            value = update_data[field]
            if isinstance(value, str):
                value = value.strip()
            setattr(connection, field, value)

        if "password" in update_data:
            connection.password = update_data["password"]

        connection.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(connection)
        logger.info("Database connection updated: connection_id=%s", connection.connection_id)
        return connection

    def delete_connection(self, db: Session, connection_id: str) -> None:
        connection = self.get_connection(db, connection_id)
        db.delete(connection)
        db.commit()
        logger.info("Database connection deleted: connection_id=%s", connection_id)

    def to_response(self, connection: AgentDbConnectionModel) -> dict[str, Any]:
        return {
            "id": connection.id,
            "connection_id": connection.connection_id,
            "user_id": connection.user_id,
            "name": connection.name,
            "db_type": connection.db_type,
            "host": connection.host,
            "port": connection.port,
            "database_name": connection.database_name,
            "username": connection.username,
            "ssl_mode": connection.ssl_mode,
            "readonly": connection.readonly,
            "status": connection.status,
            "extra": connection.extra,
            "has_password": bool(connection.password),
            "last_tested_at": connection.last_tested_at,
            "last_test_success": connection.last_test_success,
            "last_test_message": connection.last_test_message,
            "created_at": connection.created_at,
            "updated_at": connection.updated_at,
        }

    def _validate_connection_data(self, data: dict[str, Any], partial: bool) -> None:
        required_fields = ["name", "host", "database_name", "username", "password"]
        if not partial:
            missing_fields = [field for field in required_fields if not data.get(field)]
            if missing_fields:
                raise ValueError(f"missing required fields: {', '.join(missing_fields)}")

        for field in ["name", "host", "database_name", "username", "password"]:
            if field in data and isinstance(data[field], str) and not data[field].strip():
                raise ValueError(f"{field} cannot be empty")

        db_type = data.get("db_type")
        if db_type is not None:
            self._normalize_db_type(db_type)

        if "port" in data and data["port"] is not None:
            port = int(data["port"])
            if port <= 0 or port > 65535:
                raise ValueError("port must be between 1 and 65535")

        ssl_mode = data.get("ssl_mode")
        if ssl_mode is not None and ssl_mode not in SUPPORTED_SSL_MODES:
            raise ValueError("unsupported ssl_mode")

        status = data.get("status")
        if status is not None and status not in SUPPORTED_STATUSES:
            raise ValueError("status must be active or disabled")

        extra = data.get("extra")
        if extra is not None and not isinstance(extra, dict):
            raise ValueError("extra must be an object")

    def _new_connection_id(self) -> str:
        return f"dbc_{uuid.uuid4().hex}"

    def _normalize_db_type(self, db_type: str | None) -> str:
        normalized = (db_type or "postgresql").strip().lower()
        if normalized not in SUPPORTED_DB_TYPES:
            raise ValueError("db_type only supports postgresql or mysql")
        return normalized

    def _resolve_port(self, port: int | None, db_type: str) -> int:
        if port is None:
            return DEFAULT_PORTS[db_type]
        return int(port)


db_connection_service = DbConnectionService()
