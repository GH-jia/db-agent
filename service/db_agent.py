import json
import logging
import re
from typing import Any

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

    def generate_sql(
        self,
        user_message: str,
        db_type: str,
        schema_text: str,
        conversation_context: str = "",
    ) -> str:
        logger.info(
            "Generate SQL from natural language: input_length=%s db_type=%s",
            len(user_message),
            db_type,
        )
        knowledge_context = knowledge_base.build_context(user_message, top_k=3)
        system_message = self._build_system_message(
            db_type=db_type,
            schema_text=schema_text,
            knowledge_context=knowledge_context,
            conversation_context=conversation_context,
        )
        sql = chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0,
        )
        cleaned_sql = self._clean_sql(sql)
        logger.info("Generated SQL: %s", cleaned_sql)
        return cleaned_sql

    def classify_intent(self, user_message: str, conversation_context: str = "") -> str:
        normalized = user_message.strip().lower()
        metadata_keywords = [
            "元数据",
            "表结构",
            "有哪些表",
            "所有表",
            "字段",
            "列",
            "主键",
            "schema",
            "metadata",
            "table structure",
            "columns",
        ]
        data_keywords = [
            "查询",
            "统计",
            "多少",
            "几个",
            "列表",
            "数据",
            "记录",
            "最大",
            "最小",
            "最高",
            "最低",
            "平均",
            "排序",
            "select",
            "count",
            "sum",
            "avg",
            "max",
            "min",
        ]
        follow_up_keywords = [
            "那",
            "这些",
            "这个",
            "上面",
            "刚才",
            "再",
            "继续",
            "它",
            "they",
            "those",
            "that",
        ]

        if any(keyword in normalized for keyword in metadata_keywords):
            return "metadata_query"
        if any(keyword in normalized for keyword in data_keywords):
            return "data_query"
        if conversation_context and any(keyword in normalized for keyword in follow_up_keywords):
            return "data_query"
        return "chat"

    def summarize_metadata(
        self,
        user_message: str,
        schema_text: str,
        conversation_context: str = "",
    ) -> str:
        system_message = (
            "你是数据库 agent。请根据数据库元数据信息回答用户问题。"
            "回答要简洁、清楚，只说明表、字段、主键等元数据信息。"
            "不要编造不存在的表或字段。不要暴露密码、连接串、API Key。\n\n"
            f"最近对话上下文：\n{conversation_context or '无'}\n\n"
            f"数据库元数据：\n{schema_text}"
        )
        return chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0,
        )

    def summarize_query_result(
        self,
        user_message: str,
        sql: str,
        rows: list[dict[str, Any]],
        conversation_context: str = "",
    ) -> str:
        preview_rows = rows[:20]
        system_message = (
            "你是数据库 agent。请根据 SQL 查询结果用自然语言回答用户问题。"
            "回答要通俗、准确、简洁。"
            "如果结果为空，直接说明没有查询到匹配数据。"
            "不要暴露数据库密码、连接串、API Key 或其他敏感信息。\n\n"
            f"最近对话上下文：\n{conversation_context or '无'}\n\n"
            f"SQL：\n{sql}\n\n"
            f"总行数：{len(rows)}\n"
            f"结果预览 JSON：\n{json.dumps(preview_rows, ensure_ascii=False, default=str)}"
        )
        return chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0,
        )

    def answer_general_chat(
        self,
        user_message: str,
        schema_text: str,
        conversation_context: str = "",
    ) -> str:
        system_message = (
            "你是数据库 agent。用户可能在咨询数据库、表数据或元数据。"
            "如果问题不需要查询数据库，就直接回答；如果需要查询表数据，请提示用户明确查询目标。"
            "不要编造查询结果，不要暴露敏感信息。\n\n"
            f"最近对话上下文：\n{conversation_context or '无'}\n\n"
            f"当前数据库元数据：\n{schema_text}"
        )
        return chat_bot.complete_once(
            system_message=system_message,
            user_input=user_message,
            temperature=0.2,
        )

    def _build_system_message(
        self,
        db_type: str,
        schema_text: str,
        knowledge_context: str,
        conversation_context: str = "",
    ) -> str:
        db_label = self._db_label(db_type)
        return (
            f"你是一个 {db_label} SQL 助手。"
            "请根据用户问题生成一条可以执行的 SQL。"
            "只允许查询，不允许写操作。"
            "不要生成 INSERT、UPDATE、DELETE、DROP、TRUNCATE、ALTER 等写入或破坏性 SQL。"
            "只返回 SQL 本身，不要 Markdown，不要解释，不要多条语句。\n\n"
            f"目标数据库元数据：\n{schema_text}\n\n"
            f"最近对话上下文：\n{conversation_context or '无'}\n\n"
            "本地知识库检索结果如下。"
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
