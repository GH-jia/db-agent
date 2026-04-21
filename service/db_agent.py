import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from service.chat_llm import chat_bot


logger = logging.getLogger(__name__)


class DBAgentService:
    def __init__(self) -> None:
        self.schema_text = (
            "数据库中目前有一张表：\n"
            "items(\n"
            "  id integer primary key,\n"
            "  name varchar not null,\n"
            "  price float not null\n"
            ")"
        )
        self.forbidden_keywords = [
            "INSERT",
            "UPDATE",
            "DELETE",
            "DROP",
            "ALTER",
            "TRUNCATE",
            "CREATE",
            "GRANT",
            "REVOKE",
        ]

    def generate_sql(self, user_message: str) -> str:
        logger.info("Generate SQL from natural language: input_length=%s", len(user_message))
        system_message = (
            "你是一个 PostgreSQL SQL 助手。"
            "请根据用户问题生成一条可执行的 SQL。"
            "只允许查询，不允许写操作。"
            "只返回 SQL 本身，不要 Markdown，不要解释，不要多条语句。\n\n"
            f"{self.schema_text}"
        )
        sql = chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0,
        )
        cleaned_sql = self._clean_sql(sql)
        logger.info("Generated SQL: %s", cleaned_sql)
        return cleaned_sql

    def _clean_sql(self, sql: str) -> str:
        cleaned_sql = sql.strip()
        if cleaned_sql.startswith("```"):
            cleaned_sql = cleaned_sql.replace("```sql", "").replace("```", "").strip()
        return cleaned_sql.rstrip(";").strip()

    def validate_sql(self, sql: str) -> None:
        if not sql:
            raise ValueError("模型没有返回 SQL")

        normalized_sql = " ".join(sql.upper().split())
        if not normalized_sql.startswith("SELECT"):
            raise ValueError("当前版本只允许执行 SELECT 查询")

        for keyword in self.forbidden_keywords:
            if keyword in normalized_sql:
                raise ValueError(f"SQL 中包含禁止关键字: {keyword}")

        if ";" in sql:
            raise ValueError("当前版本不允许多条 SQL 语句")

        logger.info("SQL validation passed")

    def execute_query(self, db: Session, sql: str) -> list[dict[str, Any]]:
        logger.info("Execute SQL query")
        result = db.execute(text(sql))
        rows = [dict(row) for row in result.mappings().all()]
        logger.info("SQL query finished: row_count=%s", len(rows))
        return rows


db_agent_service = DBAgentService()
