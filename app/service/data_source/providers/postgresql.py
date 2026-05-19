from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.service.data_source.providers.base import DataSourceProvider
from app.service.data_source.schemas import DataSourceConfig


class PostgreSqlDataSourceProvider(DataSourceProvider):
    db_type = "postgresql"

    def build_url(self, config: DataSourceConfig) -> str:
        return (
            f"postgresql+psycopg2://{quote_plus(config.username)}:{quote_plus(config.password)}"
            f"@{config.host}:{config.port}/{quote_plus(config.database_name)}"
        )

    def build_connect_args(self, config: DataSourceConfig) -> dict[str, str]:
        if config.ssl_mode and config.ssl_mode != "disable":
            return {"sslmode": config.ssl_mode}
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
                    CASE WHEN tc.constraint_type = 'PRIMARY KEY' THEN true ELSE false END
                        AS is_primary_key
                FROM information_schema.columns c
                JOIN information_schema.tables t
                    ON t.table_schema = c.table_schema
                    AND t.table_name = c.table_name
                LEFT JOIN information_schema.key_column_usage kcu
                    ON kcu.table_schema = c.table_schema
                    AND kcu.table_name = c.table_name
                    AND kcu.column_name = c.column_name
                LEFT JOIN information_schema.table_constraints tc
                    ON tc.constraint_schema = kcu.constraint_schema
                    AND tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = c.table_schema
                    AND tc.table_name = c.table_name
                    AND tc.constraint_type = 'PRIMARY KEY'
                WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema')
                    AND t.table_type IN ('BASE TABLE', 'VIEW')
                ORDER BY c.table_schema, c.table_name, c.ordinal_position
                """
            )
        )
        return self._format_metadata([dict(row) for row in result.mappings().all()])
