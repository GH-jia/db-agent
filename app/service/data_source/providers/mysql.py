from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.service.data_source.providers.base import DataSourceProvider
from app.service.data_source.schemas import DataSourceConfig


class MySqlDataSourceProvider(DataSourceProvider):
    db_type = "mysql"

    def build_url(self, config: DataSourceConfig) -> str:
        return (
            f"mysql+pymysql://{quote_plus(config.username)}:{quote_plus(config.password)}"
            f"@{config.host}:{config.port}/{quote_plus(config.database_name)}?charset=utf8mb4"
        )

    def build_connect_args(self, config: DataSourceConfig) -> dict[str, object]:
        if config.ssl_mode in {"require", "verify-ca", "verify-full"}:
            return {"ssl": {}}
        return {}

    def get_metadata(self, session: Session, config: DataSourceConfig) -> str:
        result = session.execute(
            text(
                """
                SELECT
                    c.table_schema,
                    c.table_name,
                    c.column_name,
                    c.data_type,
                    c.is_nullable,
                    CASE WHEN kcu.constraint_name = 'PRIMARY' THEN true ELSE false END
                        AS is_primary_key
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON t.table_schema = c.table_schema
                    AND t.table_name = c.table_name
                LEFT JOIN information_schema.key_column_usage kcu
                    ON kcu.table_schema = c.table_schema
                    AND kcu.table_name = c.table_name
                    AND kcu.column_name = c.column_name
                    AND kcu.constraint_name = 'PRIMARY'
                WHERE c.table_schema = :database_name
                    AND t.table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY c.table_schema, c.table_name, c.ordinal_position
                """
            ),
            {"database_name": config.database_name},
        )
        return self._format_metadata([dict(row) for row in result.mappings().all()])
