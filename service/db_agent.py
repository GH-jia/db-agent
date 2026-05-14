import logging
import re

from service.chat_llm import chat_bot
from service.knowledge_base import knowledge_base


logger = logging.getLogger(__name__)


class DBAgentService:
    def __init__(self) -> None:
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

    def generate_sql(self, user_message: str, db_type: str, schema_text: str) -> str:
        logger.info(
            "Generate SQL from natural language: input_length=%s db_type=%s",
            len(user_message),
            db_type,
        )
        knowledge_context = knowledge_base.build_context(user_message, top_k=3)
        system_message = self._build_system_message(db_type, schema_text, knowledge_context)
        sql = chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0,
        )
        cleaned_sql = self._clean_sql(sql)
        logger.info("Generated SQL: %s", cleaned_sql)
        return cleaned_sql

    def _build_system_message(self, db_type: str, schema_text: str, knowledge_context: str) -> str:
        db_label = self._db_label(db_type)
        return (
            f"你是一个 {db_label} SQL 助手。"
            "请根据用户问题生成一条可以执行的 SQL。"
            "只允许查询，不允许写操作。"
            "不要生成 `INSERT`、`UPDATE`、`DELETE`、`DROP`、`TRUNCATE`、`ALTER` 等写入或破坏性 SQL。"
            "只返回 SQL 本身，不要 Markdown，不要解释，不要多条语句。\n\n"
            "下面是目标数据库的元数据信息：\n"
            f"{schema_text}\n\n"
            "下面是从本地知识库检索到的业务知识。"
            "如果知识库内容和用户问题相关，请优先参考；如果不相关，可以忽略。\n\n"
            f"{knowledge_context}"
        )

    def _db_label(self, db_type: str) -> str:
        labels = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
        }
        return labels.get(db_type, db_type)

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
            if re.search(rf"\b{keyword}\b", normalized_sql):
                raise ValueError(f"SQL 中包含禁止关键字: {keyword}")

        if ";" in sql:
            raise ValueError("当前版本不允许多条 SQL 语句")

        logger.info("SQL validation passed")


db_agent_service = DBAgentService()
