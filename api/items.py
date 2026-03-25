from typing import Generator

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal
from models import ItemModel


router = APIRouter()


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
    return {"message": "item created", "item": new_item}


@router.get("/items/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="item not found")
    return item


@router.put("/items/{item_id}")
def update_item(item_id: int, item: ItemUpdate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="item not found")

    db_item.name = item.name
    db_item.price = item.price
    db.commit()
    db.refresh(db_item)
    return {"message": "item updated", "item": db_item}


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="item not found")

    db.delete(db_item)
    db.commit()
    return {"message": "item deleted"}

