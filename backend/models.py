from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from .database import Base

class Workshop(Base):
    __tablename__ = "workshops"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    location = Column(String)

    items = relationship("Item", back_populates="workshop")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    items = relationship("Item", back_populates="category")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))
    workshop_id = Column(Integer, ForeignKey("workshops.id"))
    quantity = Column(Integer, default=0)
    min_quantity = Column(Integer, default=5)
    sku = Column(String)

    category = relationship("Category", back_populates="items")
    workshop = relationship("Workshop", back_populates="items")
    logs = relationship("InventoryLog", back_populates="item", cascade="all, delete-orphan")

class InventoryLog(Base):
    __tablename__ = "inventory_log"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    change_amount = Column(Integer)
    timestamp = Column(DateTime, default=func.now())
    reason = Column(String)

    item = relationship("Item", back_populates="logs")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Integer)
    status = Column(String, default="Pending") # Pending, Completed
    created_at = Column(DateTime, default=func.now())

    item = relationship("Item", backref="orders")
