import uvicorn
from fastapi import FastAPI

from api.chat import router as chat_router
from api.items import router as items_router
from database import Base, engine


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(items_router)
app.include_router(chat_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
