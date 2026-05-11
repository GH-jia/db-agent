import logging
import time

import uvicorn
from fastapi import FastAPI, Request
from logging_config import setup_logging

setup_logging()

from api.agent import router as agent_router
from api.chat import router as chat_router
from api.items import router as items_router
from database import Base, engine


logger = logging.getLogger(__name__)

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(items_router)
app.include_router(chat_router)
app.include_router(agent_router)


@app.on_event("startup")
def on_startup() -> None:
    logger.info("FastAPI application started")


@app.on_event("shutdown")
def on_shutdown() -> None:
    logger.info("FastAPI application stopped")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled request error: method=%s path=%s",
            request.method,
            request.url.path,
        )
        raise

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    level = logging.INFO if response.status_code < 400 else logging.WARNING

    logger.log(
        level,
        "HTTP request completed: method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
