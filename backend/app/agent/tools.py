from langchain_core.tools import tool
from app.database.connection import SessionLocal
from app.database.models import (
    Product, Inventory, DemandForecast, PurchaseOrder, 
    Supplier, SupplierProduct, Budget, StorageCapacity
)
from datetime import datetime, date, timedelta
import uuid


@tool
def get_product_info(product_id: str) -> str:
    """Get detailed product information including name, SKU, category, pricing, and stock level requirements.
    
    Args:
        product_id: The product ID (e.g., 'PRD-001')
    """
    db = SessionLocal()
    try:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return f"Product {product_id} not found."
        return (
            f"Product: {p.name} (ID: {p.id}, SKU: {p.sku})\n"
            f"Category: {p.category}\n"
            f"Unit Cost: ${p.unit_cost:.2f}\n"
            f"Selling Price: ${p.selling_price:.2f}\n"
            f"Margin: ${p.selling_price - p.unit_cost:.2f} ({((p.selling_price - p.unit_cost) / p.selling_price * 100):.1f}%)\n"
            f"Min Stock Level: {p.min_stock_level} units\n"
            f"Max Stock Level: {p.max_stock_level} units\n"
            f"Storage Volume Per Unit: {p.storage_volume_per_unit} m³"
        )
    finally:
        db.close()


@tool
def get_inventory_status(product_id: str, node_id: str) -> str:
    """Get current inventory status for a product at a specific fulfillment node.
    Shows current stock, reserved stock, and available stock.
    
    Args:
        product_id: The product ID (e.g., 'PRD-001')
        node_id: The fulfillment node ID (e.g., 'NODE-NORTH')
    """
    db = SessionLocal()
    try:
        inv = db.query(Inventory).filter(
            Inventory.product_id == product_id,
            Inventory.node_id == node_id
        ).first()
        if not inv:
            return f"No inventory record found for {product_id} at {node_id}."
        
        product = db.query(Product).filter(Product.id == product_id).first()
        product_name = product.name if product else product_id
        
        status = "CRITICAL" if inv.available_stock < (product.min_stock_level if product else 0) else "HEALTHY"
        
        return (
            f"Inventory Status for {product_name} at {node_id}:\n"
            f"Current Stock: {inv.current_stock} units\n"
            f"Reserved Stock: {inv.reserved_stock} units\n"
            f"Available Stock: {inv.available_stock} units\n"
            f"Min Stock Level: {product.min_stock_level if product else 'N/A'} units\n"
            f"Status: {status}"
        )
    finally:
        db.close()


@tool
def get_demand_forecast(product_id: str, node_id: str) -> str:
    """Get demand forecast data for a product at a specific node.
    Shows forecasted demand, actual demand (if available), daily demand rate, and confidence.
    
    Args:
        product_id: The product ID (e.g., 'PRD-001')
        node_id: The fulfillment node ID (e.g., 'NODE-NORTH')
    """
    db = SessionLocal()
    try:
        forecasts = db.query(DemandForecast).filter(
            DemandForecast.product_id == product_id,
            DemandForecast.node_id == node_id
        ).all()
        if not forecasts:
            return f"No demand forecast found for {product_id} at {node_id}."
        
        result_parts = [f"Demand Forecasts for {product_id} at {node_id}:"]
        for f in forecasts:
            days_in_period = (f.period_end - f.period_start).days or 7
            daily_forecasted = f.forecasted_demand / days_in_period
            
            part = (
                f"\nPeriod: {f.period_start} to {f.period_end} ({days_in_period} days)\n"
                f"  Forecasted Demand: {f.forecasted_demand} units (total period)\n"
                f"  Daily Forecasted Demand: {daily_forecasted:.1f} units/day\n"
                f"  Confidence: {f.confidence*100:.0f}%"
            )
            if f.actual_demand is not None:
                daily_actual = f.actual_demand / days_in_period
                deviation = ((f.actual_demand - f.forecasted_demand) / f.forecasted_demand * 100)
                part += (
                    f"\n  Actual Demand: {f.actual_demand} units (total period)\n"
                    f"  Daily Actual Demand: {daily_actual:.1f} units/day\n"
                    f"  Deviation from Forecast: {deviation:+.1f}%"
                )
                if abs(deviation) > 50:
                    part += f"\n  ⚠️ SIGNIFICANT DEMAND ANOMALY DETECTED"
            else:
                part += f"\n  Actual Demand: Not yet recorded"
            result_parts.append(part)
        
        return "\n".join(result_parts)
    finally:
        db.close()


@tool  
def get_open_purchase_orders(product_id: str = None, node_id: str = None) -> str:
    """Get all open/active purchase orders, optionally filtered by product and/or node.
    Shows order details including quantity, status, supplier, and expected delivery.
    
    Args:
        product_id: Optional product ID to filter by
        node_id: Optional node ID to filter by
    """
    db = SessionLocal()
    try:
        query = db.query(PurchaseOrder).filter(
            PurchaseOrder.status.in_(['pending', 'confirmed', 'partial'])
        )
        if product_id:
            query = query.filter(PurchaseOrder.product_id == product_id)
        if node_id:
            query = query.filter(PurchaseOrder.node_id == node_id)
        
        orders = query.all()
        if not orders:
            return f"No open purchase orders found" + (f" for {product_id}" if product_id else "") + "."
        
        total_incoming = sum(o.quantity_ordered for o in orders)
        result_parts = [f"Open Purchase Orders ({len(orders)} found, {total_incoming} total units incoming):"]
        
        for o in orders:
            days_until_delivery = (o.expected_delivery - date.today()).days if o.expected_delivery else "Unknown"
            supplier = db.query(Supplier).filter(Supplier.id == o.supplier_id).first()
            supplier_name = supplier.name if supplier else o.supplier_id
            
            part = (
                f"\n  PO {o.id}:\n"
                f"    Product: {o.product_id} | Supplier: {supplier_name}\n"
                f"    Quantity Ordered: {o.quantity_ordered} units\n"
                f"    Quantity Confirmed: {o.quantity_confirmed or 'Awaiting confirmation'} units\n"
                f"    Status: {o.status.upper()}\n"
                f"    Unit Price: ${o.unit_price:.2f} | Total Cost: ${o.total_cost:.2f}\n"
                f"    Expected Delivery: {o.expected_delivery} ({days_until_delivery} days from now)\n"
                f"    Created By: {o.created_by}"
            )
            if o.notes:
                part += f"\n    Notes: {o.notes}"
            result_parts.append(part)
        
        return "\n".join(result_parts)
    finally:
        db.close()


@tool
def get_supplier_info(supplier_id: str) -> str:
    """Get detailed supplier information including lead time, order constraints, and reliability.
    
    Args:
        supplier_id: The supplier ID (e.g., 'SUP-001')
    """
    db = SessionLocal()
    try:
        s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not s:
            return f"Supplier {supplier_id} not found."
        
        products = db.query(SupplierProduct).filter(SupplierProduct.supplier_id == supplier_id).all()
        product_info = []
        for sp in products:
            p = db.query(Product).filter(Product.id == sp.product_id).first()
            product_info.append(f"{p.name if p else sp.product_id} (${sp.unit_price:.2f}/unit, priority: {sp.priority})")
        
        reliability_label = "Excellent" if s.reliability_score >= 0.95 else "Good" if s.reliability_score >= 0.90 else "Fair" if s.reliability_score >= 0.85 else "Poor"
        
        return (
            f"Supplier: {s.name} (ID: {s.id})\n"
            f"Lead Time: {s.lead_time_days} days\n"
            f"Min Order Quantity (MOQ): {s.min_order_qty} units\n"
            f"Max Order Quantity: {s.max_order_qty} units\n"
            f"Reliability Score: {s.reliability_score:.2f} ({reliability_label})\n"
            f"Active: {'Yes' if s.active else 'No'}\n"
            f"Products Supplied:\n" + "\n".join(f"  - {pi}" for pi in product_info)
        )
    finally:
        db.close()


@tool
def get_suppliers_for_product(product_id: str) -> str:
    """Find all suppliers that can supply a specific product, with pricing and priority information.
    Useful for finding alternative suppliers.
    
    Args:
        product_id: The product ID (e.g., 'PRD-001')
    """
    db = SessionLocal()
    try:
        supplier_products = db.query(SupplierProduct).filter(
            SupplierProduct.product_id == product_id
        ).order_by(SupplierProduct.priority).all()
        
        if not supplier_products:
            return f"No suppliers found for product {product_id}."
        
        product = db.query(Product).filter(Product.id == product_id).first()
        product_name = product.name if product else product_id
        
        result_parts = [f"Suppliers for {product_name} ({product_id}):"]
        for sp in supplier_products:
            supplier = db.query(Supplier).filter(Supplier.id == sp.supplier_id).first()
            if not supplier or not supplier.active:
                continue
            result_parts.append(
                f"\n  {supplier.name} (ID: {supplier.id}):\n"
                f"    Unit Price: ${sp.unit_price:.2f}\n"
                f"    Priority: {sp.priority} ({'Primary' if sp.priority == 1 else 'Secondary' if sp.priority == 2 else 'Tertiary'})\n"
                f"    Lead Time: {supplier.lead_time_days} days\n"
                f"    MOQ: {supplier.min_order_qty} units | Max: {supplier.max_order_qty} units\n"
                f"    Reliability: {supplier.reliability_score:.2f}"
            )
        
        return "\n".join(result_parts)
    finally:
        db.close()


@tool
def get_budget_status(node_id: str) -> str:
    """Get the current budget status for a fulfillment node.
    Shows total budget, spent amount, and remaining budget.
    
    Args:
        node_id: The fulfillment node ID (e.g., 'NODE-NORTH')
    """
    db = SessionLocal()
    try:
        budget = db.query(Budget).filter(Budget.node_id == node_id).first()
        if not budget:
            return f"No budget information found for {node_id}."
        
        utilization = (budget.spent / budget.total_budget * 100) if budget.total_budget else 0
        status = "CRITICAL" if utilization > 90 else "WARNING" if utilization > 75 else "HEALTHY"
        
        return (
            f"Budget Status for {node_id}:\n"
            f"Category: {budget.category}\n"
            f"Total Budget: ${budget.total_budget:,.2f}\n"
            f"Spent: ${budget.spent:,.2f}\n"
            f"Remaining: ${budget.remaining:,.2f}\n"
            f"Utilization: {utilization:.1f}%\n"
            f"Status: {status}"
        )
    finally:
        db.close()


@tool
def get_storage_capacity(node_id: str) -> str:
    """Get the current storage capacity status for a fulfillment node.
    Shows total capacity, used capacity, and available capacity.
    
    Args:
        node_id: The fulfillment node ID (e.g., 'NODE-NORTH')
    """
    db = SessionLocal()
    try:
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
        if not storage:
            return f"No storage information found for {node_id}."
        
        utilization = (storage.used_units / storage.total_capacity_units * 100) if storage.total_capacity_units else 0
        status = "CRITICAL" if utilization > 90 else "WARNING" if utilization > 75 else "HEALTHY"
        
        return (
            f"Storage Capacity for {node_id}:\n"
            f"Total Capacity: {storage.total_capacity_units} units\n"
            f"Used: {storage.used_units} units\n"
            f"Available: {storage.available_units} units\n"
            f"Utilization: {utilization:.1f}%\n"
            f"Status: {status}"
        )
    finally:
        db.close()


@tool
def create_purchase_order(product_id: str, supplier_id: str, node_id: str, quantity: int, notes: str = "") -> str:
    """Create a new purchase order. Returns the created PO details.
    
    Args:
        product_id: The product ID to order
        supplier_id: The supplier to order from
        node_id: The fulfillment node for delivery
        quantity: Number of units to order
        notes: Optional notes for the purchase order
    """
    db = SessionLocal()
    try:
        # Get supplier pricing
        sp = db.query(SupplierProduct).filter(
            SupplierProduct.supplier_id == supplier_id,
            SupplierProduct.product_id == product_id
        ).first()
        
        if not sp:
            return f"Error: Supplier {supplier_id} does not carry product {product_id}."
        
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        if not supplier:
            return f"Error: Supplier {supplier_id} not found."
        
        unit_price = sp.unit_price
        total_cost = unit_price * quantity
        expected_delivery = date.today() + timedelta(days=supplier.lead_time_days)
        po_id = f"PO-{datetime.now().strftime('%Y')}-{uuid.uuid4().hex[:6].upper()}"
        
        po = PurchaseOrder(
            id=po_id,
            product_id=product_id,
            supplier_id=supplier_id,
            node_id=node_id,
            quantity_ordered=quantity,
            quantity_confirmed=None,
            unit_price=unit_price,
            total_cost=total_cost,
            status='pending',
            expected_delivery=expected_delivery,
            created_by='agent',
            notes=notes or f"Auto-created by AI Purchasing Agent"
        )
        db.add(po)
        
        # Update budget
        budget = db.query(Budget).filter(Budget.node_id == node_id).first()
        if budget:
            budget.spent += total_cost
            budget.remaining -= total_cost
        
        # Update storage (reserved)
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
        if storage:
            storage.used_units += quantity
            storage.available_units -= quantity
        
        db.commit()
        
        return (
            f"✅ Purchase Order Created Successfully:\n"
            f"PO ID: {po_id}\n"
            f"Product: {product_id}\n"
            f"Supplier: {supplier.name} ({supplier_id})\n"
            f"Quantity: {quantity} units\n"
            f"Unit Price: ${unit_price:.2f}\n"
            f"Total Cost: ${total_cost:,.2f}\n"
            f"Expected Delivery: {expected_delivery}\n"
            f"Status: PENDING"
        )
    except Exception as e:
        db.rollback()
        return f"Error creating purchase order: {str(e)}"
    finally:
        db.close()


@tool
def modify_purchase_order(order_id: str, new_quantity: int = None, new_status: str = None, notes: str = "") -> str:
    """Modify an existing purchase order's quantity or status.
    
    Args:
        order_id: The purchase order ID to modify
        new_quantity: New quantity (optional)
        new_status: New status: 'pending', 'confirmed', 'partial', 'cancelled' (optional)
        notes: Additional notes explaining the modification
    """
    db = SessionLocal()
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not po:
            return f"Error: Purchase order {order_id} not found."
        
        changes = []
        old_cost = po.total_cost
        
        if new_quantity is not None and new_quantity != po.quantity_ordered:
            old_qty = po.quantity_ordered
            po.quantity_ordered = new_quantity
            po.total_cost = new_quantity * po.unit_price
            changes.append(f"Quantity: {old_qty} → {new_quantity} units")
            changes.append(f"Total Cost: ${old_cost:.2f} → ${po.total_cost:.2f}")
            
            # Update budget with cost difference
            cost_diff = po.total_cost - old_cost
            budget = db.query(Budget).filter(Budget.node_id == po.node_id).first()
            if budget:
                budget.spent += cost_diff
                budget.remaining -= cost_diff
            
            # Update storage
            qty_diff = new_quantity - old_qty
            storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == po.node_id).first()
            if storage:
                storage.used_units += qty_diff
                storage.available_units -= qty_diff
        
        if new_status and new_status != po.status:
            old_status = po.status
            po.status = new_status
            if new_status == 'confirmed':
                po.quantity_confirmed = po.quantity_ordered
            changes.append(f"Status: {old_status} → {new_status}")
        
        if notes:
            po.notes = (po.notes + " | " + notes) if po.notes else notes
        
        po.updated_at = datetime.utcnow()
        db.commit()
        
        return (
            f"✅ Purchase Order {order_id} Modified:\n" +
            "\n".join(f"  - {c}" for c in changes) +
            (f"\nNotes: {notes}" if notes else "")
        )
    except Exception as e:
        db.rollback()
        return f"Error modifying purchase order: {str(e)}"
    finally:
        db.close()


@tool
def cancel_purchase_order(order_id: str, reason: str) -> str:
    """Cancel a purchase order and release the reserved budget and storage.
    
    Args:
        order_id: The purchase order ID to cancel
        reason: Reason for cancellation
    """
    db = SessionLocal()
    try:
        po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
        if not po:
            return f"Error: Purchase order {order_id} not found."
        
        po.status = 'cancelled'
        po.notes = (po.notes + " | CANCELLED: " + reason) if po.notes else f"CANCELLED: {reason}"
        po.updated_at = datetime.utcnow()
        
        # Release budget
        budget = db.query(Budget).filter(Budget.node_id == po.node_id).first()
        if budget:
            budget.spent -= po.total_cost
            budget.remaining += po.total_cost
        
        # Release storage
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == po.node_id).first()
        if storage:
            storage.used_units -= po.quantity_ordered
            storage.available_units += po.quantity_ordered
        
        db.commit()
        
        return (
            f"✅ Purchase Order {order_id} Cancelled:\n"
            f"Reason: {reason}\n"
            f"Budget Released: ${po.total_cost:,.2f}\n"
            f"Storage Released: {po.quantity_ordered} units"
        )
    except Exception as e:
        db.rollback()
        return f"Error cancelling purchase order: {str(e)}"
    finally:
        db.close()
