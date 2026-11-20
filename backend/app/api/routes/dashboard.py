from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.session import get_db
from app.models.entities import Product, Order, Customer

router = APIRouter(prefix="/dashboard", tags=["Tableau de bord"])


@router.get("/stats")
def stats(db: Session = Depends(get_db)):
    return {
        "products": db.query(func.count(Product.id)).filter(Product.active.is_(True)).scalar() or 0,
        "orders": db.query(func.count(Order.id)).scalar() or 0,
        "customers": db.query(func.count(Customer.id)).scalar() or 0,
        "revenue": db.query(func.coalesce(func.sum(Order.total), 0)).filter(Order.status != "Annulée").scalar() or 0,
        "pending_orders": db.query(func.count(Order.id)).filter(Order.status == "En attente").scalar() or 0,
    }
