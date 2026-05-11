import logging
from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ItemModel


router = APIRouter()
logger = logging.getLogger(__name__)


class ItemCreate(BaseModel):
    name: str
    price: float


class ItemUpdate(BaseModel):
    name: str
    price: float


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/items")
def get_items(
    keyword: str = "",
    page: int = 1,
    db: Session = Depends(get_db),
):
    logger.info("List items: keyword=%s page=%s", keyword, page)
    query = db.query(ItemModel)
    if keyword:
        query = query.filter(ItemModel.name.ilike(f"%{keyword}%"))

    items = query.order_by(ItemModel.id).all()
    return {"keyword": keyword, "page": page, "data": items}


@router.post("/items")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    new_item = ItemModel(name=item.name, price=item.price)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    logger.info("Item created: id=%s name=%s", new_item.id, new_item.name)
    return {"message": "item created", "item": new_item}


@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        logger.warning("Item not found: id=%s", item_id)
        raise HTTPException(status_code=404, detail="item not found")
    logger.info("Get item: id=%s", item_id)
    return item


@router.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        logger.warning("Item not found for update: id=%s", item_id)
        raise HTTPException(status_code=404, detail="item not found")

    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    logger.info("Item updated: id=%s", item_id)
    return {"message": "item updated", "item": db_item}


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        logger.warning("Item not found for delete: id=%s", item_id)
        raise HTTPException(status_code=404, detail="item not found")

    db.delete(db_item)
    db.commit()
    logger.info("Item deleted: id=%s", item_id)
    return {"message": "item deleted"}

