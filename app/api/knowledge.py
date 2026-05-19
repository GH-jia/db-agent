import logging

from fastapi import APIRouter
from pydantic import BaseModel

from app.service.knowledge_base import knowledge_base


router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 3


@router.post("/rebuild")
def rebuild_knowledge():
    result = knowledge_base.rebuild_vector_store()
    logger.info(
        "Knowledge vector store rebuilt: collection=%s chunk_count=%s upserted_count=%s",
        result["collection_name"],
        result["chunk_count"],
        result["upserted_count"],
    )
    return result


@router.post("/search")
def search_knowledge(request: KnowledgeSearchRequest):
    top_k = min(max(request.top_k, 1), 10)
    results = knowledge_base.search(request.query, top_k=top_k)
    logger.info("Knowledge search API completed: top_k=%s result_count=%s", top_k, len(results))
    return {
        "query": request.query,
        "top_k": top_k,
        "data": [
            {
                "source": result.source,
                "title": result.title,
                "content": result.content,
                "score": result.score,
            }
            for result in results
        ],
    }
