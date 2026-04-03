from backend.database import SessionLocal
from backend import models

db = SessionLocal()
categories = db.query(models.Category).all()
print("Categories:")
for c in categories:
    print(f"ID: {c.id}, Name: '{c.name}'")

items = db.query(models.Item).all()
print("\nItems:")
for i in items:
    print(f"ID: {i.id}, Name: '{i.name}', CategoryID: {i.category_id}, WorkshopID: {i.workshop_id}")
