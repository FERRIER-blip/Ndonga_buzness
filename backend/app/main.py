from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import Base, engine, SessionLocal
from app.models import Product
from app.api.routes import products, orders, dashboard, whatsapp, health, chat


def seed_products():
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            db.add_all([
                Product(name="Écouteurs Bluetooth", description="Écouteurs sans fil – produit de démonstration.",
                        category="Électronique", price=7500, stock=12),
                Product(name="Montre connectée", description="Montre connectée – produit de démonstration.",
                        category="Accessoires", price=15000, stock=8),
                Product(name="Sac urbain", description="Sac polyvalent – produit de démonstration.",
                        category="Mode", price=10000, stock=15),
            ])
            db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_products()
    yield


app = FastAPI(
    title=settings.app_name,
    description="API de gestion commerciale et assistant WhatsApp Ndonga_buzness",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(whatsapp.router, prefix="/api")
app.include_router(chat.router, prefix="/api")


@app.get("/")
def root():
    return {"application": "Ndonga_buzness", "status": "active", "docs": "/docs"}
