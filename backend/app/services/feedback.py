"""Feedback loop engine for post-execution verification.

Verifies that the outcome of an agent action matches expectations
and detects discrepancies between expected and actual state.
"""

from app.database.connection import SessionLocal
from app.database.models import (
    Product, Inventory, PurchaseOrder, Supplier, SupplierProduct,
    Budget, StorageCapacity, DemandForecast
)
from datetime import date


def build_context_for_validation(product_id: str, node_id: str) -> dict:
    """Build the context dict needed for validation rules."""
    db = SessionLocal()
    try:
        context = {"product_id": product_id, "node_id": node_id}
        
        # Get product info
        product = db.query(Product).filter(Product.id == product_id).first()
        if product:
            context["product_name"] = product.name
            context["unit_cost"] = product.unit_cost
        
        # Get inventory
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.node_id == node_id
        ).first()
        if inventory:
            context["available_stock"] = inventory.available_stock
            context["current_stock"] = inventory.current_stock
        
        # Get demand forecast
        forecast = db.query(DemandForecast).filter(
            DemandForecast.product_id == product_id,
            DemandForecast.node_id == node_id
        ).first()
        if forecast:
            days = max((forecast.period_end - forecast.period_start).days, 1)
            actual = forecast.actual_demand if forecast.actual_demand else forecast.forecasted_demand
            daily_demand = actual / days
            context["daily_demand"] = daily_demand
            context["coverage_days"] = inventory.available_stock / daily_demand if daily_demand > 0 and inventory else 0
        
        # Get primary supplier info
        sp = db.query(SupplierProduct).filter(
            SupplierProduct.product_id == product_id
        ).order_by(SupplierProduct.priority).first()
        if sp:
            context["unit_price"] = sp.unit_price
            supplier = db.query(Supplier).filter(Supplier.id == sp.supplier_id).first()
            if supplier:
                context["min_order_qty"] = supplier.min_order_qty
                context["max_order_qty"] = supplier.max_order_qty
                context["lead_time_days"] = supplier.lead_time_days
                context["supplier_id"] = supplier.id
        
        # Get budget
        budget = db.query(Budget).filter(Budget.node_id == node_id).first()
        if budget:
            context["remaining_budget"] = budget.remaining
        
        # Get storage
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
        if storage:
            context["available_storage"] = storage.available_units
        
        # Count existing open POs
        existing_pos = db.query(PurchaseOrder).filter(
            PurchaseOrder.product_id == product_id,
            PurchaseOrder.node_id == node_id,
            PurchaseOrder.status.in_(["pending", "confirmed", "partial"])
        ).count()
        context["existing_pos"] = existing_pos
        
        return context
    finally:
        db.close()


def verify_execution(product_id: str, node_id: str, decision: dict, execution_result: dict) -> dict:
    """Verify that execution produced the expected results.
    
    This is the core of the feedback loop — it checks post-execution state
    against what we expected to happen.
    """
    db = SessionLocal()
    try:
        verification = {
            "verified": True,
            "checks": [],
            "discrepancies": "",
            "summary": ""
        }
        
        decision_type = decision.get("decision_type", "")
        
        if decision_type in ["reject", "escalate"]:
            verification["summary"] = f"Decision was '{decision_type}' — no execution to verify."
            verification["checks"].append({"check": "Decision type", "passed": True, "detail": f"{decision_type} requires no execution"})
            return verification
        
        # Check 1: Was the action executed successfully?
        if not execution_result or not execution_result.get("success"):
            verification["verified"] = False
            verification["discrepancies"] = "Execution reported failure."
            verification["checks"].append({"check": "Execution success", "passed": False, "detail": "Action did not complete successfully"})
            return verification
        
        verification["checks"].append({"check": "Execution success", "passed": True, "detail": "Action completed successfully"})
        
        # Check 2: Verify PO exists in database
        recent_po = db.query(PurchaseOrder).filter(
            PurchaseOrder.product_id == product_id,
            PurchaseOrder.node_id == node_id,
            PurchaseOrder.created_by == "agent"
        ).order_by(PurchaseOrder.created_at.desc()).first()
        
        if decision_type in ["accept", "modify"] and not recent_po:
            verification["verified"] = False
            verification["discrepancies"] = "Expected a new PO to exist but none found."
            verification["checks"].append({"check": "PO exists", "passed": False, "detail": "No agent-created PO found"})
            return verification
        
        if recent_po:
            verification["checks"].append({"check": "PO exists in database", "passed": True, "detail": f"PO {recent_po.id} found in database"})
            
            # Check 3: PO quantity is reasonable
            expected_qty = decision.get("recommended_quantity")
            if expected_qty and abs(recent_po.quantity_ordered - expected_qty) > expected_qty * 0.1:
                verification["verified"] = False
                verification["discrepancies"] += f"PO quantity mismatch: expected ~{expected_qty}, got {recent_po.quantity_ordered}. "
                verification["checks"].append({"check": "Quantity match", "passed": False, "detail": f"Expected ~{expected_qty}, got {recent_po.quantity_ordered}"})
            else:
                verification["checks"].append({"check": "Quantity match", "passed": True, "detail": f"PO quantity: {recent_po.quantity_ordered} units"})
            
            # Check 4: Budget still non-negative
            budget = db.query(Budget).filter(Budget.node_id == node_id).first()
            if budget and budget.remaining < 0:
                verification["verified"] = False
                verification["discrepancies"] += f"Budget went negative: ${budget.remaining:,.2f}. "
                verification["checks"].append({"check": "Budget integrity", "passed": False, "detail": f"Budget is negative: ${budget.remaining:,.2f}"})
            else:
                remaining = f"${budget.remaining:,.2f}" if budget else "N/A"
                verification["checks"].append({"check": "Budget integrity", "passed": True, "detail": f"Budget remaining: {remaining}"})
            
            # Check 5: Storage not exceeded
            storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
            if storage and storage.available_units < 0:
                verification["verified"] = False
                verification["discrepancies"] += f"Storage exceeded: {abs(storage.available_units)} units over capacity. "
                verification["checks"].append({"check": "Storage integrity", "passed": False, "detail": f"Storage over capacity by {abs(storage.available_units)} units"})
            else:
                avail = f"{storage.available_units} units" if storage else "N/A"
                verification["checks"].append({"check": "Storage integrity", "passed": True, "detail": f"Storage available: {avail}"})
        
        # Build summary
        passed_checks = sum(1 for c in verification["checks"] if c["passed"])
        total_checks = len(verification["checks"])
        verification["summary"] = f"{passed_checks}/{total_checks} post-execution checks passed."
        
        return verification
    finally:
        db.close()


def calculate_inventory_projection(current_stock: int, incoming_orders: int, daily_demand: float, days_ahead: int) -> list:
    """Project inventory levels over the next N days."""
    projection = []
    stock = float(current_stock + incoming_orders)
    for day in range(days_ahead):
        stock -= daily_demand
        projection.append({"day": day + 1, "projected_stock": max(0, round(stock, 1))})
        if stock <= 0:
            projection[-1]["stockout"] = True
    return projection


def detect_discrepancy(expected: dict, actual: dict) -> list:
    """Compare expected state vs actual state and return discrepancies."""
    discrepancies = []
    for key in expected:
        if key in actual and expected[key] != actual[key]:
            discrepancies.append({
                "field": key,
                "expected": expected[key],
                "actual": actual[key],
                "delta": actual[key] - expected[key] if isinstance(expected[key], (int, float)) else None
            })
    return discrepancies
