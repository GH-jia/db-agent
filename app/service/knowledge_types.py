from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    title: str
    content: str
    chunk_index: int


@dataclass(frozen=True)
class KnowledgeSearchResult:
    source: str
    title: str
    content: str
    score: float
