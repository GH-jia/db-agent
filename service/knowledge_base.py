import logging
import re
from pathlib import Path
from typing import Any

from service.embedding import embedding_service
from service.knowledge_types import KnowledgeChunk, KnowledgeSearchResult
from service.qdrant_store import qdrant_knowledge_store


logger = logging.getLogger(__name__)


class FileKnowledgeBase:
    def __init__(self, knowledge_dir: Path | None = None) -> None:
        self.knowledge_dir = knowledge_dir or Path(__file__).resolve().parent.parent / "knowledge"

    def rebuild_vector_store(self) -> dict[str, Any]:
        chunks = self._load_chunks()
        qdrant_knowledge_store.delete_markdown_points()
        if not chunks:
            logger.warning("No knowledge chunks found: dir=%s", self.knowledge_dir)
            return {
                "collection_name": qdrant_knowledge_store.collection_name,
                "chunk_count": 0,
                "upserted_count": 0,
            }

        embedding_inputs = [self._build_embedding_text(chunk) for chunk in chunks]
        vectors = embedding_service.embed_texts(embedding_inputs)
        upserted_count = qdrant_knowledge_store.upsert_chunks(chunks, vectors)
        return {
            "collection_name": qdrant_knowledge_store.collection_name,
            "chunk_count": len(chunks),
            "upserted_count": upserted_count,
        }

    def search(self, query: str, top_k: int = 3) -> list[KnowledgeSearchResult]:
        query = query.strip()
        if not query:
            return []

        query_vector = embedding_service.embed_text(query)
        return qdrant_knowledge_store.search(query_vector, top_k=top_k)

    def build_context(self, query: str, top_k: int = 3) -> str:
        results = self.search(query, top_k=top_k)
        if not results:
            return "没有检索到相关知识库内容。"

        blocks = []
        for index, result in enumerate(results, start=1):
            blocks.append(
                "\n".join(
                    [
                        f"[知识片段 {index}]",
                        f"来源：{result.source}",
                        f"标题：{result.title}",
                        result.content,
                    ]
                )
            )
        return "\n\n".join(blocks)

    def _load_chunks(self) -> list[KnowledgeChunk]:
        if not self.knowledge_dir.exists():
            logger.warning("Knowledge directory does not exist: %s", self.knowledge_dir)
            return []

        chunks: list[KnowledgeChunk] = []
        for path in sorted(self.knowledge_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            chunks.extend(self._split_markdown(path.name, text, start_index=len(chunks)))
        return chunks

    def _split_markdown(self, source: str, text: str, start_index: int = 0) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        title = Path(source).stem
        lines: list[str] = []

        def flush() -> None:
            content_lines = [line for line in lines if line.strip()]
            has_body = any(not re.match(r"^#{1,6}\s+.+$", line) for line in content_lines)
            content = "\n".join(content_lines).strip()
            if not has_body:
                return
            if content:
                chunks.append(
                    KnowledgeChunk(
                        source=source,
                        title=title,
                        content=content,
                        chunk_index=start_index + len(chunks),
                    )
                )

        for raw_line in text.splitlines():
            line = raw_line.rstrip()
            heading = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading:
                flush()
                title = heading.group(2).strip()
                lines = [line]
                continue
            lines.append(line)

        flush()
        return chunks

    def _build_embedding_text(self, chunk: KnowledgeChunk) -> str:
        return "\n".join(
            [
                f"来源：{chunk.source}",
                f"标题：{chunk.title}",
                chunk.content,
            ]
        )


knowledge_base = FileKnowledgeBase()
