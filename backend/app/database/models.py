from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, JSON
from sqlalchemy.orm import relationship
from .connection import Base
from datetime import datetime

class Product(Base):
    __tablename__ = "products"
    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    sku = Column(String, unique=True, index=True)
    category = Column(String)
    unit_cost = Column(Float)
    selling_price = Column(Float)
    min_stock_level = Column(Integer)
    max_stock_level = Column(Integer)
    storage_volume_per_unit = Column(Float)

class InventoryNode(Base):
    __tablename__ = "inventory_nodes"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    location = Column(String)

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey("products.id"))
    node_id = Column(String, ForeignKey("inventory_nodes.id"))
    current_stock = Column(Integer)
    reserved_stock = Column(Integer)
    available_stock = Column(Integer)

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    lead_time_days = Column(Integer)
    min_order_qty = Column(Integer)
    max_order_qty = Column(Integer)
    reliability_score = Column(Float)
    active = Column(Boolean, default=True)
    products_supplied = Column(JSON)

class SupplierProduct(Base):
    __tablename__ = "supplier_products"
    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    product_id = Column(String, ForeignKey("products.id"))
    unit_price = Column(Float)
    priority = Column(Integer)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(String, primary_key=True, index=True)
    product_id = Column(String, ForeignKey("products.id"))
    supplier_id = Column(String, ForeignKey("suppliers.id"))
    node_id = Column(String, ForeignKey("inventory_nodes.id"))
    quantity_ordered = Column(Integer)
    quantity_confirmed = Column(Integer, nullable=True)
    unit_price = Column(Float)
    total_cost = Column(Float)
    status = Column(String)
    expected_delivery = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = Column(String, nullable=True)
    created_by = Column(String)

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, ForeignKey("products.id"))
    node_id = Column(String, ForeignKey("inventory_nodes.id"))
    period_start = Column(Date)
    period_end = Column(Date)
    forecasted_demand = Column(Integer)
    actual_demand = Column(Integer, nullable=True)
    confidence = Column(Float)

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, ForeignKey("inventory_nodes.id"))
    category = Column(String)
    total_budget = Column(Float)
    spent = Column(Float)
    remaining = Column(Float)

class StorageCapacity(Base):
    __tablename__ = "storage_capacities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String, ForeignKey("inventory_nodes.id"))
    total_capacity_units = Column(Integer)
    used_units = Column(Integer)
    available_units = Column(Integer)

class AgentDecision(Base):
    __tablename__ = "agent_decisions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    scenario_type = Column(String)
    decision_type = Column(String)
    original_recommendation = Column(JSON)
    agent_analysis = Column(JSON)
    final_decision = Column(JSON)
    validation_results = Column(JSON)
    execution_result = Column(JSON, nullable=True)
    feedback_loop_log = Column(JSON, nullable=True)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
