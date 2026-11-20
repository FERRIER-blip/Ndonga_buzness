from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.entities import Product, Customer, Order, OrderItem
from app.schemas.orders import OrderCreate, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Commandes"])
VALID_STATUSES = {"En attente", "Confirmée", "En préparation", "Expédiée", "Terminée", "Annulée"}


def serialize_order(order):
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "total": order.total,
        "notes": order.notes,
        "created_at": order.created_at.isoformat(),
        "customer_name": order.customer.name,
        "phone": order.customer.phone,
        "item_count": sum(item.quantity for item in order.items),
    }


@router.get("")
def list_orders(db: Session = Depends(get_db)):
    return [serialize_order(o) for o in db.query(Order).order_by(Order.id.desc()).all()]


@router.post("", status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.phone == payload.phone).first()
    if not customer:
        customer = Customer(name=payload.customer_name, phone=payload.phone, address=payload.address)
        db.add(customer)
        db.flush()
    else:
        customer.name = payload.customer_name
        customer.address = payload.address

    order = Order(order_number=f"NDG-{uuid4().hex[:8].upper()}",
                  customer_id=customer.id, notes=payload.notes, status="En attente")
    total = 0.0
    db.add(order)
    db.flush()

    for item in payload.items:
        product = db.get(Product, item.product_id)
        if not product or not product.active:
            raise HTTPException(status_code=400, detail=f"Produit {item.product_id} indisponible")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"Stock insuffisant pour {product.name}")
        product.stock -= item.quantity
        total += product.price * item.quantity
        order.items.append(OrderItem(product_id=product.id, quantity=item.quantity, unit_price=product.price))

    order.total = round(total, 2)
    db.commit()
    db.refresh(order)
    return serialize_order(order)


@router.patch("/{order_id}/status")
def update_status(order_id: int, payload: OrderStatusUpdate, db: Session = Depends(get_db)):
    if payload.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Statut non reconnu")
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    order.status = payload.status
    db.commit()
    db.refresh(order)
    return serialize_order(order)
