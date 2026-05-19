import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from app.service.data_source.providers.base import DataSourceProvider
from app.service.data_source.providers.mysql import MySqlDataSourceProvider
from app.service.data_source.providers.postgresql import PostgreSqlDataSourceProvider
from app.service.data_source.schemas import DataSourceConfig


logger = logging.getLogger(__name__)


class DataSourceError(Exception):
    pass


class DataSourceManager:
    def __init__(self) -> None:
        providers = [
            PostgreSqlDataSourceProvider(),
            MySqlDataSourceProvider(),
        ]
        self._providers = {provider.db_type: provider for provider in providers}

    @contextmanager
    def session_scope(self, config: DataSourceConfig) -> Generator[Session, None, None]:
        provider = self._get_provider(config.db_type)
        self._validate_config(config)
        engine = provider.create_engine(config)
        session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = session_factory()
        try:
            yield session
        finally:
            session.close()
            engine.dispose()

    def execute_query(self, config: DataSourceConfig, sql: str) -> list[dict[str, Any]]:
        provider = self._get_provider(config.db_type)
        with self.session_scope(config) as session:
            logger.info(
                "Execute target database query: connection_id=%s db_type=%s",
                config.connection_id,
                config.db_type,
            )
            rows = provider.execute_query(session, sql)
            logger.info(
                "Target database query finished: connection_id=%s row_count=%s",
                config.connection_id,
                len(rows),
            )
            return rows

    def get_metadata(self, config: DataSourceConfig) -> str:
        provider = self._get_provider(config.db_type)
        with self.session_scope(config) as session:
            logger.info(
                "Load target database metadata: connection_id=%s db_type=%s",
                config.connection_id,
                config.db_type,
            )
            return provider.get_metadata(session, config)

    def _get_provider(self, db_type: str) -> DataSourceProvider:
        provider = self._providers.get(db_type)
        if not provider:
            raise DataSourceError(f"unsupported db_type: {db_type}")
        return provider

    def _validate_config(self, config: DataSourceConfig) -> None:
        if config.status != "active":
            raise DataSourceError("database connection is disabled")


data_source_manager = DataSourceManager()
