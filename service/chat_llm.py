import logging
from collections.abc import Generator
from pathlib import Path

import yaml
from openai import OpenAI


logger = logging.getLogger(__name__)


def _load_api_key_from_config() -> str:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config.get("API_KEY", "")


class ChatBot:
    def __init__(self, api_key: str, model: str = "glm-4.6v"):
        self.api_key = api_key
        self.model = model
        self.sessions: dict[str, list[dict[str, str]]] = {}
        self._client: OpenAI | None = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            logger.info("Create OpenAI client: model=%s", self.model)
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
            )
        return self._client

    def _create_system_message(self) -> dict[str, str]:
        return {"role": "system", "content": "你是一个有帮助的 AI 助手。"}

    def _get_conversation(self, session_id: str) -> list[dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = [self._create_system_message()]
        return self.sessions[session_id]

    def complete_once(
        self,
        system_message: str,
        user_input: str,
        temperature: float = 0,
    ) -> str:
        logger.info("Call LLM complete_once: input_length=%s", len(user_input))
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input},
            ],
            temperature=temperature,
        )
        return (response.choices[0].message.content or "").strip()

    def stream_chat(self, session_id: str, user_input: str) -> Generator[str, None, None]:
        logger.info(
            "Call LLM stream_chat: session_id=%s input_length=%s",
            session_id,
            len(user_input),
        )
        conversation = self._get_conversation(session_id)
        conversation.append({"role": "user", "content": user_input})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=conversation,
            stream=True,
            temperature=0.8,
        )

        assistant_reply_parts: list[str] = []
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                assistant_reply_parts.append(delta)
                yield delta

        assistant_reply = "".join(assistant_reply_parts)
        conversation.append({"role": "assistant", "content": assistant_reply})
        logger.info(
            "LLM stream_chat finished: session_id=%s output_length=%s",
            session_id,
            len(assistant_reply),
        )

    def clear_history(self, session_id: str) -> None:
        self.sessions[session_id] = [self._create_system_message()]
        logger.info("Local chat session cleared: session_id=%s", session_id)


chat_bot = ChatBot(api_key=_load_api_key_from_config())
