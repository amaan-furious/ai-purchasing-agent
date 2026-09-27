from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import PurchaseOrder
from app.api.schemas import PurchaseOrderResponse
import uuid

router = APIRouter()

@router.get("/api/orders", response_model=list[PurchaseOrderResponse])
def list_orders(status: str = None, product_id: str = None, db: Session = Depends(get_db)):
    query = db.query(PurchaseOrder)
    if status: query = query.filter(PurchaseOrder.status == status)
    if product_id: query = query.filter(PurchaseOrder.product_id == product_id)
    return query.all()

@router.get("/api/orders/{order_id}", response_model=PurchaseOrderResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()

@router.post("/api/orders", response_model=PurchaseOrderResponse)
def create_order(order: dict, db: Session = Depends(get_db)):
    new_order = PurchaseOrder(**order)
    if not new_order.id: new_order.id = str(uuid.uuid4())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.put("/api/orders/{order_id}", response_model=PurchaseOrderResponse)
def update_order(order_id: str, update_data: dict, db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    for key, value in update_data.items():
        setattr(order, key, value)
    db.commit()
    db.refresh(order)
    return order

@router.delete("/api/orders/{order_id}")
def cancel_order(order_id: str, reason: str, db: Session = Depends(get_db)):
    order = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    order.status = 'cancelled'
    order.notes = reason
    db.commit()
    return {"status": "cancelled"}
