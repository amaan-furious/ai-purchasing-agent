from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from .models import (
    Product, InventoryNode, Inventory, Supplier, SupplierProduct,
    PurchaseOrder, DemandForecast, Budget, StorageCapacity, Base, AgentDecision
)
from .connection import engine

def seed_database(db: Session):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Products
    products = [
        Product(id='PRD-001', name='Organic Whole Milk 1L', sku='SKU001', category='Dairy', unit_cost=2.50, selling_price=4.99, min_stock_level=200, max_stock_level=2000, storage_volume_per_unit=0.001),
        Product(id='PRD-002', name='Free-Range Eggs (12pk)', sku='SKU002', category='Dairy', unit_cost=3.20, selling_price=6.49, min_stock_level=150, max_stock_level=1500, storage_volume_per_unit=0.002),
        Product(id='PRD-003', name='Artisan Sourdough Bread', sku='SKU003', category='Bakery', unit_cost=1.80, selling_price=4.29, min_stock_level=100, max_stock_level=800, storage_volume_per_unit=0.003),
        Product(id='PRD-004', name='Premium Orange Juice 1L', sku='SKU004', category='Beverages', unit_cost=2.00, selling_price=4.49, min_stock_level=250, max_stock_level=2500, storage_volume_per_unit=0.001),
        Product(id='PRD-005', name='Greek Yogurt 500g', sku='SKU005', category='Dairy', unit_cost=1.50, selling_price=3.99, min_stock_level=200, max_stock_level=1800, storage_volume_per_unit=0.0005),
        Product(id='PRD-006', name='Organic Bananas (bunch)', sku='SKU006', category='Fresh Produce', unit_cost=1.20, selling_price=2.99, min_stock_level=300, max_stock_level=3000, storage_volume_per_unit=0.002),
        Product(id='PRD-007', name='Fresh Atlantic Salmon 500g', sku='SKU007', category='Seafood', unit_cost=8.00, selling_price=14.99, min_stock_level=50, max_stock_level=500, storage_volume_per_unit=0.001),
        Product(id='PRD-008', name='Avocado (each)', sku='SKU008', category='Fresh Produce', unit_cost=0.80, selling_price=2.49, min_stock_level=400, max_stock_level=4000, storage_volume_per_unit=0.0003),
    ]
    db.add_all(products)

    # Nodes
    nodes = [
        InventoryNode(id='NODE-NORTH', name='North Fulfillment Center', location='Chicago'),
        InventoryNode(id='NODE-SOUTH', name='South Fulfillment Center', location='Miami'),
        InventoryNode(id='NODE-WEST', name='West Fulfillment Center', location='Los Angeles'),
    ]
    db.add_all(nodes)

    # Suppliers
    suppliers = [
        Supplier(id='SUP-001', name='Fresh Farms Co.', lead_time_days=3, min_order_qty=100, max_order_qty=5000, reliability_score=0.92, active=True, products_supplied=['PRD-001', 'PRD-002', 'PRD-005', 'PRD-006']),
        Supplier(id='SUP-002', name='Coastal Distributors', lead_time_days=5, min_order_qty=200, max_order_qty=8000, reliability_score=0.88, active=True, products_supplied=['PRD-001', 'PRD-003', 'PRD-004', 'PRD-007', 'PRD-008']),
        Supplier(id='SUP-003', name='Metro Food Supply', lead_time_days=2, min_order_qty=50, max_order_qty=3000, reliability_score=0.95, active=True, products_supplied=['PRD-001', 'PRD-002', 'PRD-005', 'PRD-006']),
    ]
    db.add_all(suppliers)

    db.commit()

    # SupplierProducts
    supplier_products = [
        SupplierProduct(supplier_id='SUP-001', product_id='PRD-001', unit_price=2.50, priority=1),
        SupplierProduct(supplier_id='SUP-001', product_id='PRD-002', unit_price=3.20, priority=1),
        SupplierProduct(supplier_id='SUP-001', product_id='PRD-005', unit_price=1.50, priority=1),
        SupplierProduct(supplier_id='SUP-001', product_id='PRD-006', unit_price=1.20, priority=1),

        SupplierProduct(supplier_id='SUP-002', product_id='PRD-001', unit_price=2.65, priority=2),
        SupplierProduct(supplier_id='SUP-002', product_id='PRD-003', unit_price=1.80, priority=1),
        SupplierProduct(supplier_id='SUP-002', product_id='PRD-004', unit_price=2.00, priority=1),
        SupplierProduct(supplier_id='SUP-002', product_id='PRD-007', unit_price=8.00, priority=1),
        SupplierProduct(supplier_id='SUP-002', product_id='PRD-008', unit_price=0.80, priority=1),

        SupplierProduct(supplier_id='SUP-003', product_id='PRD-001', unit_price=2.45, priority=3),
        SupplierProduct(supplier_id='SUP-003', product_id='PRD-002', unit_price=3.35, priority=2),
        SupplierProduct(supplier_id='SUP-003', product_id='PRD-005', unit_price=1.55, priority=2),
        SupplierProduct(supplier_id='SUP-003', product_id='PRD-006', unit_price=1.25, priority=2),
    ]
    db.add_all(supplier_products)

    # Inventory
    inventory = [
        Inventory(product_id='PRD-001', node_id='NODE-NORTH', current_stock=450, reserved_stock=50, available_stock=400),
        Inventory(product_id='PRD-002', node_id='NODE-NORTH', current_stock=200, reserved_stock=30, available_stock=170),
        Inventory(product_id='PRD-003', node_id='NODE-NORTH', current_stock=80, reserved_stock=10, available_stock=70),
        Inventory(product_id='PRD-004', node_id='NODE-NORTH', current_stock=600, reserved_stock=100, available_stock=500),
        Inventory(product_id='PRD-005', node_id='NODE-NORTH', current_stock=350, reserved_stock=50, available_stock=300),
        Inventory(product_id='PRD-006', node_id='NODE-NORTH', current_stock=180, reserved_stock=20, available_stock=160),
        Inventory(product_id='PRD-007', node_id='NODE-NORTH', current_stock=45, reserved_stock=5, available_stock=40),
        Inventory(product_id='PRD-008', node_id='NODE-NORTH', current_stock=500, reserved_stock=100, available_stock=400),
    ]
    db.add_all(inventory)

    # Purchase Orders
    pos = [
        PurchaseOrder(id='PO-2026-001', product_id='PRD-001', supplier_id='SUP-001', node_id='NODE-NORTH', quantity_ordered=300, quantity_confirmed=300, unit_price=2.50, total_cost=750.0, status='confirmed', expected_delivery=date.today() + timedelta(days=2), created_by='system'),
        PurchaseOrder(id='PO-2026-002', product_id='PRD-004', supplier_id='SUP-002', node_id='NODE-NORTH', quantity_ordered=500, quantity_confirmed=None, unit_price=2.00, total_cost=1000.0, status='pending', expected_delivery=date.today() + timedelta(days=5), created_by='system'),
        PurchaseOrder(id='PO-2026-003', product_id='PRD-006', supplier_id='SUP-001', node_id='NODE-NORTH', quantity_ordered=200, quantity_confirmed=200, unit_price=1.20, total_cost=240.0, status='confirmed', expected_delivery=date.today() + timedelta(days=3), created_by='system'),
    ]
    db.add_all(pos)

    # Forecasts
    forecasts = [
        DemandForecast(product_id='PRD-001', node_id='NODE-NORTH', period_start=date.today(), period_end=date.today() + timedelta(days=7), forecasted_demand=600, actual_demand=None, confidence=0.85),
        DemandForecast(product_id='PRD-004', node_id='NODE-NORTH', period_start=date.today(), period_end=date.today() + timedelta(days=7), forecasted_demand=400, confidence=0.80),
        DemandForecast(product_id='PRD-006', node_id='NODE-NORTH', period_start=date.today(), period_end=date.today() + timedelta(days=7), forecasted_demand=250, actual_demand=750, confidence=0.75),
    ]
    db.add_all(forecasts)

    # Budgets
    budgets = [
        Budget(node_id='NODE-NORTH', category='General', total_budget=50000.0, spent=32000.0, remaining=18000.0)
    ]
    db.add_all(budgets)

    # Storage
    storage = [
        StorageCapacity(node_id='NODE-NORTH', total_capacity_units=5000, used_units=3800, available_units=1200)
    ]
    db.add_all(storage)

    db.commit()
