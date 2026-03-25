import os
from collections.abc import Generator

from openai import OpenAI


class ChatBot:
    def __init__(self, api_key: str, model: str = "glm-4.7"):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
        )
        self.model = model
        self.sessions: dict[str, list[dict[str, str]]] = {}

    def _create_system_message(self) -> dict[str, str]:
        return {"role": "system", "content": "你是一个有帮助的 AI 助手"}

    def _get_conversation(self, session_id: str) -> list[dict[str, str]]:
        if session_id not in self.sessions:
            self.sessions[session_id] = [self._create_system_message()]
        return self.sessions[session_id]

    def stream_chat(self, session_id: str, user_input: str) -> Generator[str, None, None]:
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

    def clear_history(self, session_id: str) -> None:
        self.sessions[session_id] = [self._create_system_message()]


chat_bot = ChatBot(api_key=os.getenv("API_KEY", ""))
