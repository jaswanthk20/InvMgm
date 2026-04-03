from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# Workshop Schemas
class WorkshopBase(BaseModel):
    name: str
    location: Optional[str] = None

class WorkshopCreate(WorkshopBase):
    pass

class WorkshopUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None

class Workshop(WorkshopBase):
    id: int
    class Config:
        from_attributes = True

# Item Schemas
class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: int
    workshop_id: int
    quantity: int = 0
    min_quantity: int = 5
    sku: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    workshop_id: Optional[int] = None
    quantity: Optional[int] = None
    min_quantity: Optional[int] = None
    sku: Optional[str] = None

class Item(ItemBase):
    id: int
    category: Category
    workshop: Workshop
    class Config:
        from_attributes = True

# Log Schemas
class InventoryLogBase(BaseModel):
    item_id: int
    change_amount: int
    reason: Optional[str] = None

class InventoryLogCreate(InventoryLogBase):
    pass

class InventoryLog(InventoryLogBase):
    id: int
    timestamp: datetime
    class Config:
        from_attributes = True

# Order Schemas
class OrderBase(BaseModel):
    item_id: int
    quantity: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    status: str
    created_at: datetime
    item: Item
    class Config:
        from_attributes = True
