import os

from fastapi import FastAPI
from openai import OpenAI

from api.items import router as items_router
from database import Base, engine


app = FastAPI()

Base.metadata.create_all(bind=engine)
app.include_router(items_router)


class ChatBot:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://open.bigmodel.cn/api/paas/v4/",
        )
        self.conversation = [
            {"role": "system", "content": "你是一个有帮助的 AI 助手"}
        ]

    def chat(self, user_input: str) -> str:
        # 1. 先把用户本轮问题放入历史消息
        self.conversation.append({"role": "user", "content": user_input})

        # 2. 调用大模型，使用完整历史消息实现多轮对话
        response = self.client.chat.completions.create(
            model="glm-4.7",
            messages=self.conversation,
            stream=True,
            temperature=0.8,
        )

        # 3. 一边流式输出，一边把本轮 AI 回复完整拼接起来
        assistant_reply_parts = []
        for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                print(delta, end="", flush=True)
                assistant_reply_parts.append(delta)

        print()

        # 4. 把 AI 完整回复加入历史，下一轮才能继续上下文
        assistant_reply = "".join(assistant_reply_parts)
        self.conversation.append({"role": "assistant", "content": assistant_reply})

        return assistant_reply

    def clear_history(self):
        """清除对话历史，但保留 system 提示词。"""
        self.conversation = self.conversation[:1]


if __name__ == "__main__":
    api_key = os.getenv("API_KEY")
    bot = ChatBot(api_key)

    first_answer = bot.chat("你好，请介绍一下自己")
    print("第一轮完整回复：", first_answer)

    second_answer = bot.chat("你能基于你上一轮的回答，继续展开说明吗？")
    print("第二轮完整回复：", second_answer)
