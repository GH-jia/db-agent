import logging
from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from service.data_source.schemas import DataSourceConfig


logger = logging.getLogger(__name__)


class DataSourceProvider(ABC):
    db_type: str

    def create_engine(self, config: DataSourceConfig) -> Engine:
        return create_engine(
            self.build_url(config),
            connect_args=self.build_connect_args(config),
            pool_pre_ping=True,
        )

    def build_connect_args(self, config: DataSourceConfig) -> dict[str, Any]:
        return {}

    def execute_query(self, session: Session, sql: str) -> list[dict[str, Any]]:
        result = session.execute(text(sql))
        return [dict(row) for row in result.mappings().all()]

    @abstractmethod
    def build_url(self, config: DataSourceConfig) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_metadata(self, session: Session, config: DataSourceConfig) -> str:
        raise NotImplementedError

    def _format_metadata(self, rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "No user tables were found in the selected database."

        table_map: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for row in rows:
            key = (row["table_schema"], row["table_name"])
            table_map.setdefault(key, []).append(row)

        lines = ["Database schema:"]
        for (table_schema, table_name), columns in table_map.items():
            lines.append(f"{table_schema}.{table_name}(")
            for column in columns:
                nullable = "nullable" if column["is_nullable"] == "YES" else "not null"
                primary_key = " primary key" if column.get("is_primary_key") else ""
                lines.append(
                    f"  {column['column_name']} {column['data_type']} {nullable}{primary_key}"
                )
            lines.append(")")

        return "\n".join(lines)
