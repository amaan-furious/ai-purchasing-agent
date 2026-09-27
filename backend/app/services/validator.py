"""Deterministic validation engine for purchasing decisions.

These rules are NOT LLM-based — they use exact mathematical checks
to ensure business constraints are respected.
"""

from app.database.connection import SessionLocal
from app.database.models import (
    Budget, StorageCapacity, Supplier, SupplierProduct, PurchaseOrder, Inventory
)


def _get_effective_supplier_id(supplier_id: str | None, product_id: str | None, db) -> str | None:
    if supplier_id:
        return supplier_id
    if product_id:
        sp = db.query(SupplierProduct).filter(SupplierProduct.product_id == product_id).order_by(SupplierProduct.priority).first()
        if sp:
            return sp.supplier_id
    return None


def _budget_check(decision: dict, context: dict) -> dict:
    """Check if the purchase fits within the remaining budget."""
    quantity = decision.get("recommended_quantity", 0)
    if not quantity or decision.get("decision_type") in ["reject", "escalate"]:
        return {"rule_name": "Budget Constraint", "passed": True, "details": "N/A for rejected/escalated decision"}
        
    db = SessionLocal()
    try:
        node_id = context.get("node_id")
        product_id = context.get("product_id")
        budget = db.query(Budget).filter(Budget.node_id == node_id).first()
        if not budget:
            return {"rule_name": "Budget Constraint", "passed": False, "details": f"No budget found for node {node_id}"}
        
        supplier_id = _get_effective_supplier_id(decision.get("recommended_supplier_id"), product_id, db)
        if not supplier_id:
            return {"rule_name": "Budget Constraint", "passed": False, "details": "No supplier identified"}
        
        sp = db.query(SupplierProduct).filter(
            SupplierProduct.supplier_id == supplier_id,
            SupplierProduct.product_id == product_id
        ).first()
        
        if not sp:
            return {"rule_name": "Budget Constraint", "passed": False, "details": f"Supplier pricing not found for supplier {supplier_id}"}
            
        cost = quantity * sp.unit_price
        if cost > budget.remaining:
            return {"rule_name": "Budget Constraint", "passed": False, "details": f"Cost ${cost:,.2f} exceeds remaining budget ${budget.remaining:,.2f}"}
            
        return {"rule_name": "Budget Constraint", "passed": True, "details": f"Cost ${cost:,.2f} is within remaining budget ${budget.remaining:,.2f}"}
    finally:
        db.close()

def _storage_check(decision: dict, context: dict) -> dict:
    """Check if the purchase fits within available storage."""
    quantity = decision.get("recommended_quantity", 0)
    if not quantity or decision.get("decision_type") in ["reject", "escalate"]:
        return {"rule_name": "Storage Capacity Constraint", "passed": True, "details": "N/A for rejected/escalated decision"}

    db = SessionLocal()
    try:
        node_id = context.get("node_id")
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
        if not storage:
            return {"rule_name": "Storage Capacity Constraint", "passed": False, "details": f"No storage capacity found for node {node_id}"}
            
        if quantity > storage.available_units:
            return {"rule_name": "Storage Capacity Constraint", "passed": False, "details": f"Quantity {quantity} exceeds available storage {storage.available_units}"}
            
        return {"rule_name": "Storage Capacity Constraint", "passed": True, "details": f"Quantity {quantity} fits in available storage {storage.available_units}"}
    finally:
        db.close()

def _supplier_moq_check(decision: dict, context: dict) -> dict:
    """Check if the purchase meets the supplier's Minimum Order Quantity."""
    quantity = decision.get("recommended_quantity", 0)
    if not quantity or decision.get("decision_type") in ["reject", "escalate"]:
        return {"rule_name": "Supplier MOQ Constraint", "passed": True, "details": "N/A"}

    db = SessionLocal()
    try:
        product_id = context.get("product_id")
        supplier_id = _get_effective_supplier_id(decision.get("recommended_supplier_id"), product_id, db)
        if not supplier_id:
            return {"rule_name": "Supplier MOQ Constraint", "passed": False, "details": "No supplier specified"}
            
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return {"rule_name": "Supplier MOQ Constraint", "passed": False, "details": f"Supplier {supplier_id} not found"}
            
        if quantity < supplier.min_order_qty:
            return {"rule_name": "Supplier MOQ Constraint", "passed": False, "details": f"Quantity {quantity} is less than supplier MOQ {supplier.min_order_qty}"}
            
        if quantity > supplier.max_order_qty:
            return {"rule_name": "Supplier Max Order Constraint", "passed": False, "details": f"Quantity {quantity} exceeds supplier Max Order Qty {supplier.max_order_qty}"}
            
        return {"rule_name": "Supplier Constraint", "passed": True, "details": f"Quantity {quantity} meets MOQ ({supplier.min_order_qty}) and Max Qty ({supplier.max_order_qty}) constraints for {supplier.id}"}
    finally:
        db.close()

def run_all_validations(decision: dict, context: dict) -> list[dict]:
    """Run all validation checks and return results."""
    return [
        _budget_check(decision, context),
        _storage_check(decision, context),
        _supplier_moq_check(decision, context)
    ]
