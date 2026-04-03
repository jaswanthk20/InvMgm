from sqlalchemy.orm import Session
from . import models, schemas

def get_workshop(db: Session, workshop_id: int):
    return db.query(models.Workshop).filter(models.Workshop.id == workshop_id).first()

def get_workshops(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Workshop).offset(skip).limit(limit).all()

def create_workshop(db: Session, workshop: schemas.WorkshopCreate):
    db_workshop = models.Workshop(name=workshop.name, location=workshop.location)
    db.add(db_workshop)
    db.commit()
    db.refresh(db_workshop)
    return db_workshop

def update_workshop(db: Session, workshop_id: int, workshop_update: schemas.WorkshopUpdate):
    db_workshop = db.query(models.Workshop).filter(models.Workshop.id == workshop_id).first()
    if db_workshop:
        if workshop_update.name is not None:
            db_workshop.name = workshop_update.name
        if workshop_update.location is not None:
            db_workshop.location = workshop_update.location
        db.commit()
        db.refresh(db_workshop)
    return db_workshop

def delete_workshop(db: Session, workshop_id: int):
    # Check if workshop has items
    items = db.query(models.Item).filter(models.Item.workshop_id == workshop_id).first()
    if items:
        return None
    
    db_workshop = db.query(models.Workshop).filter(models.Workshop.id == workshop_id).first()
    if db_workshop:
        db.delete(db_workshop)
        db.commit()
    return db_workshop

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Category).offset(skip).limit(limit).all()

def create_category(db: Session, category: schemas.CategoryCreate):
    db_category = models.Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    # Check if category has items
    items = db.query(models.Item).filter(models.Item.category_id == category_id).first()
    if items:
        # Prevent deletion if items exist
        return None
    
    db_category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if db_category:
        db.delete(db_category)
        db.commit()
    return db_category

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    # Log creation
    log = models.InventoryLog(item_id=db_item.id, change_amount=item.quantity, reason="Initial Stock")
    db.add(log)
    db.commit()
    
    return db_item

def update_item_quantity(db: Session, item_id: int, quantity_change: int, reason: str):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        db_item.quantity += quantity_change
        log = models.InventoryLog(item_id=item_id, change_amount=quantity_change, reason=reason)
        db.add(log)
        db.commit()
        db.refresh(db_item)
    return db_item

def delete_item(db: Session, item_id: int):
    db_item = db.query(models.Item).filter(models.Item.id == item_id).first()
    if db_item:
        # Delete related orders first (no cascade from Order side)
        db.query(models.Order).filter(models.Order.item_id == item_id).delete()
        db.delete(db_item)  # Logs cascade via relationship
        db.commit()
    return db_item

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(item_id=order.item_id, quantity=order.quantity)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).order_by(models.Order.created_at.desc()).offset(skip).limit(limit).all()

def complete_order(db: Session, order_id: int):
    db_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if db_order and db_order.status == "Pending":
        db_order.status = "Completed"
        
        # Update Item Quantity inline (avoid double-commit from calling update_item_quantity)
        db_item = db.query(models.Item).filter(models.Item.id == db_order.item_id).first()
        if db_item:
            db_item.quantity += db_order.quantity
            log = models.InventoryLog(
                item_id=db_order.item_id,
                change_amount=db_order.quantity,
                reason=f"Order #{db_order.id} Received"
            )
            db.add(log)
        
        db.commit()
        db.refresh(db_order)
    return db_order

def get_logs(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.InventoryLog).order_by(models.InventoryLog.timestamp.desc()).offset(skip).limit(limit).all()
