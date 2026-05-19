import logging

from openai import OpenAI

from app.service.config import get_config_value


logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimension: int | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else get_config_value("API_KEY", "")
        self.model = model or get_config_value("EMBEDDING_MODEL", "Embedding-3")
        self.dimension = int(dimension or get_config_value("EMBEDDING_DIM", 1024))
        self._client: OpenAI | None = None

    # @property 是 Python 的一个装饰器，作用是：把一个方法伪装成属性来用。可以 self.client 使用，在真正使用时会调用这个方法，起到一个延迟初始化的作用
    @property
    def client(self) -> OpenAI:
        if self._client is None:
            logger.info("Create embedding client: model=%s dimension=%s", self.model, self.dimension)
            self._client = OpenAI(
                api_key=self.api_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/",
            )
        return self._client

    def embed_text(self, text: str) -> list[float]:
        return self.embed_texts([text])[0]

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        clean_texts = [text.strip() for text in texts if text.strip()]
        if not clean_texts:
            return []

        logger.info("Create embeddings: count=%s", len(clean_texts))
        response = self.client.embeddings.create(
            model=self.model,
            input=clean_texts,
            dimensions=self.dimension,
        )
        vectors = [item.embedding for item in response.data]
        for vector in vectors:
            if len(vector) != self.dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {self.dimension}, got {len(vector)}"
                )
        return vectors


embedding_service = EmbeddingService()
