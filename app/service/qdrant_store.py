import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.service.config import get_config_value
from app.service.knowledge_types import KnowledgeChunk, KnowledgeSearchResult


logger = logging.getLogger(__name__)

PROJECT_NAME = "db-agent"
SOURCE_TYPE_MARKDOWN = "markdown"


class QdrantKnowledgeStore:
    def __init__(self) -> None:
        self.host = get_config_value("QDRANT.HOST", "127.0.0.1")
        self.port = int(get_config_value("QDRANT.PORT", 6333))
        self.api_key = get_config_value("QDRANT.API_KEY", "") or None
        self.collection_name = get_config_value("QDRANT.COLLECTION_NAME", "db_agent_knowledge")
        self.dimension = int(get_config_value("EMBEDDING_DIM", 1024))
        self._client: QdrantClient | None = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            logger.info("Create Qdrant client: host=%s port=%s collection=%s", self.host, self.port, self.collection_name)
            self._client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key,
            )
        return self._client

    def ensure_collection(self) -> None:
        # { ... }，这是 Python 的集合推导式，collection_names 是一个 set 集合。 [] 是数组。tuple(collection.name for collection in ...) 是元组
        collection_names = {collection.name for collection in self.client.get_collections().collections}
        if self.collection_name in collection_names:
            return

        logger.info("Create Qdrant collection: name=%s dimension=%s", self.collection_name, self.dimension)
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(size=self.dimension, distance=Distance.COSINE),
        )

    def delete_markdown_points(self) -> None:
        logger.info("Delete managed markdown points from Qdrant")
        self.ensure_collection()
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=self._managed_markdown_filter(),
            wait=True,
        )

    def upsert_chunks(self, chunks: list[KnowledgeChunk], vectors: list[list[float]]) -> int:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors length mismatch")

        self.ensure_collection()
        points = [
            PointStruct(
                id=self._point_id(chunk),
                vector=vector,
                payload={
                    "project": PROJECT_NAME,
                    "source_type": SOURCE_TYPE_MARKDOWN,
                    "source": chunk.source,
                    "title": chunk.title,
                    "content": chunk.content,
                    "chunk_index": chunk.chunk_index,
                },
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        if not points:
            return 0

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        logger.info("Upsert Qdrant points finished: count=%s", len(points))
        return len(points)

    def search(self, query_vector: list[float], top_k: int = 3) -> list[KnowledgeSearchResult]:
        self.ensure_collection()
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=self._managed_markdown_filter(),
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        results: list[KnowledgeSearchResult] = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                KnowledgeSearchResult(
                    source=str(payload.get("source", "")),
                    title=str(payload.get("title", "")),
                    content=str(payload.get("content", "")),
                    score=float(point.score),
                )
            )
        logger.info("Qdrant search finished: result_count=%s", len(results))
        return results

    def _managed_markdown_filter(self) -> Filter:
        return Filter(
            must=[
                FieldCondition(key="project", match=MatchValue(value=PROJECT_NAME)),
                FieldCondition(key="source_type", match=MatchValue(value=SOURCE_TYPE_MARKDOWN)),
            ]
        )

    def _point_id(self, chunk: KnowledgeChunk) -> str:
        raw_id = f"{PROJECT_NAME}:{SOURCE_TYPE_MARKDOWN}:{chunk.source}:{chunk.chunk_index}"
        return str(uuid.uuid5(uuid.NAMESPACE_URL, raw_id))


qdrant_knowledge_store = QdrantKnowledgeStore()
