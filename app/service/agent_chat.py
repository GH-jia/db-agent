import logging
from decimal import Decimal
from datetime import date
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.dao.models import AgentMessageModel, AgentSessionModel
from app.service.data_source import DataSourceConfig, data_source_manager
from app.service.db_agent import db_agent_service
from app.service.db_connection import db_connection_service


logger = logging.getLogger(__name__)

ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
INTENT_DATA_QUERY = "data_query"
INTENT_METADATA_QUERY = "metadata_query"
INTENT_CHAT = "chat"


class AgentChatService:
    def chat(
        self,
        app_db: Session,
        session_id: str,
        message: str,
        connection_id: str | None = None,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        session_id = session_id.strip()
        message = message.strip()
        if not session_id:
            raise ValueError("session_id cannot be empty")
        if not message:
            raise ValueError("message cannot be empty")

        session = self._get_or_create_session(
            app_db=app_db,
            session_id=session_id,
            connection_id=connection_id,
            user_id=user_id,
            first_message=message,
        )
        resolved_connection_id = self._resolve_connection_id(
            app_db=app_db,
            session=session,
            connection_id=connection_id,
        )
        connection = db_connection_service.get_connection(app_db, resolved_connection_id)
        data_source_config = DataSourceConfig.from_model(connection)

        history = self._load_recent_messages(app_db, session_id=session.session_id, limit=10)
        conversation_context = self._build_context(history)
        intent = db_agent_service.classify_intent(message, conversation_context)
        self._save_message(
            app_db=app_db,
            session_id=session.session_id,
            role=ROLE_USER,
            content=message,
            intent=intent,
            extra={"connection_id": resolved_connection_id},
        )

        schema_text = ""
        sql = None
        data: list[dict[str, Any]] = []
        if intent == INTENT_METADATA_QUERY:
            schema_text = data_source_manager.get_metadata(data_source_config)
            answer = db_agent_service.summarize_metadata(
                user_message=message,
                schema_text=schema_text,
                conversation_context=conversation_context,
            )
        elif intent == INTENT_DATA_QUERY:
            schema_text = data_source_manager.get_metadata(data_source_config)
            sql = db_agent_service.generate_sql(
                user_message=message,
                db_type=data_source_config.db_type,
                schema_text=schema_text,
                conversation_context=conversation_context,
            )
            db_agent_service.validate_sql(sql)
            data = data_source_manager.execute_query(data_source_config, sql)
            answer = db_agent_service.summarize_query_result(
                user_message=message,
                sql=sql,
                rows=data,
                conversation_context=conversation_context,
            )
        else:
            answer = db_agent_service.answer_general_chat(
                user_message=message,
                schema_text="未查询数据库 schema。",
                conversation_context=conversation_context,
            )

        assistant_extra = {
            "connection_id": resolved_connection_id,
            "intent": intent,
            "row_count": len(data),
            "data_preview": self._json_safe(data[:20]),
            "schema_used": bool(schema_text),
        }
        if sql:
            assistant_extra["sql"] = sql

        self._save_message(
            app_db=app_db,
            session_id=session.session_id,
            role=ROLE_ASSISTANT,
            content=answer,
            intent=intent,
            sql_text=sql,
            extra=assistant_extra,
        )
        self._touch_session(app_db, session)

        logger.info(
            "Agent chat finished: session_id=%s connection_id=%s intent=%s row_count=%s",
            session.session_id,
            resolved_connection_id,
            intent,
            len(data),
        )
        return {
            "session_id": session.session_id,
            "connection_id": resolved_connection_id,
            "intent": intent,
            "answer": answer,
            "sql": sql,
            "row_count": len(data),
            "data": data,
        }

    def _get_or_create_session(
        self,
        app_db: Session,
        session_id: str,
        connection_id: str | None,
        user_id: str | None,
        first_message: str,
    ) -> AgentSessionModel:
        session = (
            app_db.query(AgentSessionModel)
            .filter(AgentSessionModel.session_id == session_id)
            .first()
        )
        if session:
            return session

        if not connection_id:
            raise ValueError("connection_id is required for the first chat request")

        db_connection_service.get_connection(app_db, connection_id.strip())
        session = AgentSessionModel(
            session_id=session_id,
            user_id=user_id,
            db_connection_id=connection_id.strip(),
            title=first_message[:100],
            status="active",
        )
        app_db.add(session)
        app_db.commit()
        app_db.refresh(session)
        logger.info("Agent session created: session_id=%s", session.session_id)
        return session

    def _resolve_connection_id(
        self,
        app_db: Session,
        session: AgentSessionModel,
        connection_id: str | None,
    ) -> str:
        if connection_id:
            resolved_connection_id = connection_id.strip()
            db_connection_service.get_connection(app_db, resolved_connection_id)
            if session.db_connection_id != resolved_connection_id:
                session.db_connection_id = resolved_connection_id
                session.updated_at = datetime.now(timezone.utc)
                app_db.commit()
                app_db.refresh(session)
            return resolved_connection_id

        if not session.db_connection_id:
            raise ValueError("connection_id is required for this chat session")
        return session.db_connection_id

    def _load_recent_messages(
        self,
        app_db: Session,
        session_id: str,
        limit: int = 10,
    ) -> list[AgentMessageModel]:
        rows = (
            app_db.query(AgentMessageModel)
            .filter(AgentMessageModel.session_id == session_id)
            .order_by(AgentMessageModel.id.desc())
            .limit(limit)
            .all()
        )
        return list(reversed(rows))

    def _build_context(self, messages: list[AgentMessageModel]) -> str:
        if not messages:
            return ""

        lines = []
        for message in messages:
            extra = message.extra or {}
            summary_parts = [
                f"role={message.role}",
                f"intent={message.intent or ''}",
                f"content={message.content}",
            ]
            if message.sql_text:
                summary_parts.append(f"sql={message.sql_text}")
            if "row_count" in extra:
                summary_parts.append(f"row_count={extra['row_count']}")
            if extra.get("data_preview"):
                summary_parts.append(f"data_preview={extra['data_preview']}")
            lines.append(" | ".join(summary_parts))
        return "\n".join(lines)

    def _save_message(
        self,
        app_db: Session,
        session_id: str,
        role: str,
        content: str,
        intent: str | None = None,
        sql_text: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> AgentMessageModel:
        message = AgentMessageModel(
            session_id=session_id,
            role=role,
            content=content,
            intent=intent,
            sql_text=sql_text,
            extra=extra or {},
        )
        app_db.add(message)
        app_db.commit()
        app_db.refresh(message)
        return message

    def _touch_session(self, app_db: Session, session: AgentSessionModel) -> None:
        session.updated_at = datetime.now(timezone.utc)
        app_db.commit()

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._json_safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self._json_safe(item) for item in value]
        if isinstance(value, tuple):
            return [self._json_safe(item) for item in value]
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value


agent_chat_service = AgentChatService()
