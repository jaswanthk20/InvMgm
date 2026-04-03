from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import models, routes
from .database import engine, SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed data
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if not db.query(models.Workshop).first():
            seed_workshops = [
                models.Workshop(name="Workshop A", location="Main Building"),
                models.Workshop(name="Workshop B", location="Annex"),
                models.Workshop(name="Workshop C", location="Off-site"),
            ]
            db.add_all(seed_workshops)
            db.commit()

        if not db.query(models.Category).first():
            seed_categories = [
                models.Category(name="Handy Tool"),
                models.Category(name="Consumable"),
                models.Category(name="Spare Part"),
            ]
            db.add_all(seed_categories)
            db.commit()
    finally:
        db.close()

    yield  # Application runs here


app = FastAPI(title="Inventory Management System", lifespan=lifespan)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

app.mount("/static", StaticFiles(directory="backend/static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('backend/static/index.html')
