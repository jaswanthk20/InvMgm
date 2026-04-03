from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/workshops/", response_model=schemas.Workshop)
def create_workshop(workshop: schemas.WorkshopCreate, db: Session = Depends(get_db)):
    return crud.create_workshop(db=db, workshop=workshop)

@router.get("/workshops/", response_model=List[schemas.Workshop])
def read_workshops(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    workshops = crud.get_workshops(db, skip=skip, limit=limit)
    return workshops

@router.put("/workshops/{workshop_id}", response_model=schemas.Workshop)
def update_workshop(workshop_id: int, workshop: schemas.WorkshopUpdate, db: Session = Depends(get_db)):
    db_workshop = crud.update_workshop(db, workshop_id=workshop_id, workshop_update=workshop)
    if db_workshop is None:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return db_workshop

@router.delete("/workshops/{workshop_id}", response_model=schemas.Workshop)
def delete_workshop(workshop_id: int, db: Session = Depends(get_db)):
    workshop = crud.delete_workshop(db, workshop_id=workshop_id)
    if workshop is None:
        raise HTTPException(status_code=400, detail="Workshop not found or contains items")
    return workshop

@router.post("/categories/", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db=db, category=category)

@router.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = crud.delete_category(db, category_id=category_id)
    if category is None:
        raise HTTPException(status_code=400, detail="Category not found or contains items")
    return category

@router.get("/categories/", response_model=List[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@router.post("/items/", response_model=schemas.Item)
def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)

@router.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)

@router.put("/items/{item_id}/quantity", response_model=schemas.Item)
def update_item_quantity(item_id: int, change: int, reason: str, db: Session = Depends(get_db)):
    item = crud.update_item_quantity(db, item_id=item_id, quantity_change=change, reason=reason)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.delete("/items/{item_id}", response_model=schemas.Item)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/orders/", response_model=schemas.Order)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    return crud.create_order(db=db, order=order)

@router.get("/orders/", response_model=List[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_orders(db, skip=skip, limit=limit)

@router.put("/orders/{order_id}/complete", response_model=schemas.Order)
def complete_order(order_id: int, db: Session = Depends(get_db)):
    order = crud.complete_order(db, order_id=order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.get("/logs/", response_model=List[schemas.InventoryLog])
def read_logs(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    logs = crud.get_logs(db, skip=skip, limit=limit)
    return logs
