from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Supplier, SupplierProduct
from app.api.schemas import SupplierResponse

router = APIRouter()

@router.get("/api/suppliers", response_model=list[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db)):
    return db.query(Supplier).all()

@router.get("/api/suppliers/{supplier_id}", response_model=SupplierResponse)
def get_supplier(supplier_id: str, db: Session = Depends(get_db)):
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()

@router.get("/api/suppliers/for-product/{product_id}", response_model=list[SupplierResponse])
def get_suppliers_for_product(product_id: str, db: Session = Depends(get_db)):
    sp_list = db.query(SupplierProduct).filter(SupplierProduct.product_id == product_id).all()
    supplier_ids = [sp.supplier_id for sp in sp_list]
    return db.query(Supplier).filter(Supplier.id.in_(supplier_ids)).all()
