from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Product, Inventory, InventoryNode

router = APIRouter()


@router.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    """List all products with full details."""
    products = db.query(Product).all()
    return [{
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "category": p.category,
        "unit_cost": p.unit_cost,
        "selling_price": p.selling_price,
        "min_stock_level": p.min_stock_level,
        "max_stock_level": p.max_stock_level,
        "storage_volume_per_unit": p.storage_volume_per_unit,
        "margin": round(p.selling_price - p.unit_cost, 2),
        "margin_pct": round((p.selling_price - p.unit_cost) / p.selling_price * 100, 1) if p.selling_price else 0
    } for p in products]


@router.get("/api/products/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get detailed product information."""
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        return {"error": "Product not found"}
    return {
        "id": p.id,
        "name": p.name,
        "sku": p.sku,
        "category": p.category,
        "unit_cost": p.unit_cost,
        "selling_price": p.selling_price,
        "min_stock_level": p.min_stock_level,
        "max_stock_level": p.max_stock_level,
        "storage_volume_per_unit": p.storage_volume_per_unit
    }


@router.get("/api/inventory/{node_id}")
def get_inventory(node_id: str, db: Session = Depends(get_db)):
    """Get all inventory for a specific node."""
    items = db.query(Inventory).filter(Inventory.node_id == node_id).all()
    result = []
    for inv in items:
        product = db.query(Product).filter(Product.id == inv.product_id).first()
        status = "CRITICAL" if inv.available_stock < (product.min_stock_level if product else 0) else "HEALTHY"
        result.append({
            "product_id": inv.product_id,
            "product_name": product.name if product else inv.product_id,
            "category": product.category if product else "",
            "node_id": inv.node_id,
            "current_stock": inv.current_stock,
            "reserved_stock": inv.reserved_stock,
            "available_stock": inv.available_stock,
            "min_stock_level": product.min_stock_level if product else 0,
            "status": status
        })
    return result


@router.get("/api/inventory/{node_id}/{product_id}")
def get_inventory_detail(node_id: str, product_id: str, db: Session = Depends(get_db)):
    """Get specific product inventory at a node."""
    inv = db.query(Inventory).filter(
        Inventory.node_id == node_id,
        Inventory.product_id == product_id
    ).first()
    if not inv:
        return {"error": "Inventory not found"}
    return {
        "product_id": inv.product_id,
        "node_id": inv.node_id,
        "current_stock": inv.current_stock,
        "reserved_stock": inv.reserved_stock,
        "available_stock": inv.available_stock
    }


@router.get("/api/nodes")
def list_nodes(db: Session = Depends(get_db)):
    """List all fulfillment nodes."""
    nodes = db.query(InventoryNode).all()
    return [{"id": n.id, "name": n.name, "location": n.location} for n in nodes]


@router.get("/api/forecasts/{node_id}")
def get_forecasts(node_id: str, db: Session = Depends(get_db)):
    """Get demand forecasts for a node."""
    from app.database.models import DemandForecast
    forecasts = db.query(DemandForecast).filter(DemandForecast.node_id == node_id).all()
    result = []
    for f in forecasts:
        product = db.query(Product).filter(Product.id == f.product_id).first()
        result.append({
            "product_id": f.product_id,
            "product_name": product.name if product else f.product_id,
            "node_id": f.node_id,
            "period_start": f.period_start.isoformat() if f.period_start else None,
            "period_end": f.period_end.isoformat() if f.period_end else None,
            "forecasted_demand": f.forecasted_demand,
            "actual_demand": f.actual_demand,
            "confidence": f.confidence,
            "has_anomaly": f.actual_demand is not None and f.actual_demand > f.forecasted_demand * 1.5
        })
    return result


@router.get("/api/budget/{node_id}")
def get_budget(node_id: str, db: Session = Depends(get_db)):
    """Get budget information for a node."""
    from app.database.models import Budget
    budget = db.query(Budget).filter(Budget.node_id == node_id).first()
    if not budget:
        return {"error": "Budget not found"}
    return {
        "node_id": budget.node_id,
        "category": budget.category,
        "total_budget": budget.total_budget,
        "spent": budget.spent,
        "remaining": budget.remaining,
        "utilization_pct": round(budget.spent / budget.total_budget * 100, 1) if budget.total_budget else 0
    }


@router.get("/api/storage/{node_id}")
def get_storage(node_id: str, db: Session = Depends(get_db)):
    """Get storage capacity information for a node."""
    from app.database.models import StorageCapacity
    storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
    if not storage:
        return {"error": "Storage not found"}
    return {
        "node_id": storage.node_id,
        "total_capacity_units": storage.total_capacity_units,
        "used_units": storage.used_units,
        "available_units": storage.available_units,
        "utilization_pct": round(storage.used_units / storage.total_capacity_units * 100, 1) if storage.total_capacity_units else 0
    }
