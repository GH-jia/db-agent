from dataclasses import dataclass, field
from typing import Any

from app.dao.models import AgentDbConnectionModel


@dataclass(frozen=True)
class DataSourceConfig:
    connection_id: str
    db_type: str
    host: str
    port: int
    database_name: str
    username: str
    password: str
    ssl_mode: str = "prefer"
    readonly: bool = True
    status: str = "active"
    extra: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_model(cls, connection: AgentDbConnectionModel) -> "DataSourceConfig":
        return cls(
            connection_id=connection.connection_id,
            db_type=connection.db_type,
            host=connection.host,
            port=connection.port,
            database_name=connection.database_name,
            username=connection.username,
            password=connection.password,
            ssl_mode=connection.ssl_mode,
            readonly=connection.readonly,
            status=connection.status,
            extra=connection.extra or {},
        )
