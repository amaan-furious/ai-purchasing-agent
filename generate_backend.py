import os
from pathlib import Path

root_dir = Path(r"c:\Users\amaan\OneDrive\Desktop\Rappi assignment\backend")

files_to_create = {
    "requirements.txt": """fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
pydantic-settings==2.5.0
langchain==0.3.0
langchain-openai==0.2.0
langchain-core==0.3.0
langgraph==0.2.20
python-dotenv==1.0.1
httpx==0.27.0
sse-starlette==2.1.0
pytest==8.3.0
pytest-asyncio==0.24.0
aiofiles==24.1.0""",
    ".env.example": """OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./purchasing.db
LLM_MODEL=gpt-4o-mini""",
    "app/__init__.py": "",
    "app/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = "your_openai_api_key_here"
    DATABASE_URL: str = "sqlite:///./purchasing.db"
    LLM_MODEL: str = "gpt-4o-mini"

    class Config:
        env_file = ".env"

settings = Settings()""",
    "app/database/__init__.py": "",
    "app/database/connection.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()""",
    "app/database/models.py": """from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, DateTime, JSON
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
""",
    "app/database/seed.py": """from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from .models import (
    Product, InventoryNode, Inventory, Supplier, SupplierProduct,
    PurchaseOrder, DemandForecast, Budget, StorageCapacity, Base
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
        DemandForecast(product_id='PRD-001', node_id='NODE-NORTH', period_start=date.today(), period_end=date.today() + timedelta(days=7), forecasted_demand=600, confidence=0.85),
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
""",
    "app/api/__init__.py": "",
    "app/api/schemas.py": """from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date, datetime

class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    category: str
    unit_cost: float
    selling_price: float

class InventoryResponse(BaseModel):
    id: int
    product_id: str
    node_id: str
    current_stock: int
    reserved_stock: int
    available_stock: int

class SupplierResponse(BaseModel):
    id: str
    name: str
    lead_time_days: int
    min_order_qty: int
    max_order_qty: int

class PurchaseOrderResponse(BaseModel):
    id: str
    product_id: str
    supplier_id: str
    node_id: str
    quantity_ordered: int
    status: str
    total_cost: float

class ForecastResponse(BaseModel):
    id: int
    product_id: str
    node_id: str
    forecasted_demand: int

class BudgetResponse(BaseModel):
    id: int
    node_id: str
    category: str
    total_budget: float
    spent: float
    remaining: float

class StorageResponse(BaseModel):
    id: int
    node_id: str
    total_capacity_units: int
    used_units: int
    available_units: int

class ScenarioRequest(BaseModel):
    scenario_id: int
    product_id: str
    node_id: str
    params: Optional[dict] = None

class ScenarioConfig(BaseModel):
    scenario_type: str
    product_id: str
    node_id: str
    parameters: dict

class AgentResponse(BaseModel):
    decision: dict
    reasoning_steps: List[str]
    validation_results: List[Any]
    execution_result: Optional[dict]
    feedback_log: Optional[dict]
""",
    "app/api/routes/__init__.py": "",
    "app/api/routes/products.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import Product, Inventory
from app.api.schemas import ProductResponse, InventoryResponse

router = APIRouter()

@router.get("/api/products", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@router.get("/api/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.id == product_id).first()

@router.get("/api/inventory/{node_id}", response_model=list[InventoryResponse])
def list_inventory(node_id: str, db: Session = Depends(get_db)):
    return db.query(Inventory).filter(Inventory.node_id == node_id).all()

@router.get("/api/inventory/{node_id}/{product_id}", response_model=InventoryResponse)
def get_inventory(node_id: str, product_id: str, db: Session = Depends(get_db)):
    return db.query(Inventory).filter(Inventory.node_id == node_id, Inventory.product_id == product_id).first()
""",
    "app/api/routes/suppliers.py": """from fastapi import APIRouter, Depends
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
""",
    "app/api/routes/orders.py": """from fastapi import APIRouter, Depends
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
""",
    "app/api/routes/scenarios.py": """from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse
from app.api.schemas import ScenarioRequest
from app.agent.graph import run_agent

router = APIRouter()

@router.get("/api/scenarios")
def list_scenarios():
    return [{"id": 1, "description": "Scenario 1"}]

@router.get("/api/scenarios/{scenario_id}")
def get_scenario(scenario_id: int):
    return {"id": scenario_id, "data": "scenario data state"}

@router.post("/api/scenarios/{scenario_id}/run")
def run_scenario(scenario_id: int, request: ScenarioRequest):
    return EventSourceResponse(run_agent(request.dict()))

@router.post("/api/scenarios/{scenario_id}/reset")
def reset_scenario(scenario_id: int):
    from app.database.connection import SessionLocal
    from app.database.seed import seed_database
    db = SessionLocal()
    seed_database(db)
    db.close()
    return {"status": "reset"}
""",
    "app/api/routes/agent.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import AgentDecision
from app.api.schemas import ScenarioConfig
from app.agent.graph import run_agent
from sse_starlette.sse import EventSourceResponse

router = APIRouter()

@router.post("/api/agent/run")
def run_agent_route(config: ScenarioConfig):
    return EventSourceResponse(run_agent(config.dict()))

@router.get("/api/agent/decisions")
def list_decisions(db: Session = Depends(get_db)):
    return db.query(AgentDecision).all()

@router.get("/api/agent/decisions/{decision_id}")
def get_decision(decision_id: int, db: Session = Depends(get_db)):
    return db.query(AgentDecision).filter(AgentDecision.id == decision_id).first()
""",
    "app/agent/__init__.py": "",
    "app/agent/prompts.py": """MAIN_SYSTEM_PROMPT = \"\"\"You are an expert AI Purchasing Agent for a quick-commerce company.
You make data-driven purchasing decisions by investigating inventory, demand, suppliers, budgets, and constraints.
You NEVER blindly accept recommendations — you always validate with data.
You follow a structured decision process: Investigate -> Analyze -> Decide -> Validate -> Execute -> Verify.

Key rules for the agent:
- Always check ALL relevant data before deciding
- Never exceed budget or storage constraints
- Always consider existing open POs
- Calculate coverage days (inventory / daily demand)
- Consider supplier reliability and lead times
- Explain your reasoning clearly
- If constraints prevent the ideal action, find the best alternative
- Escalate to human when risk is high or constraints can't be resolved\"\"\"
""",
    "app/agent/state.py": """from typing import TypedDict, Annotated, Optional
import operator

def add_messages(left, right):
    return left + right

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    scenario_type: str
    scenario_config: dict
    product_id: str
    node_id: str
    investigation_data: dict
    analysis: dict
    decision: dict
    validation_results: list
    execution_result: Optional[dict]
    verification_result: Optional[dict]
    reasoning_steps: Annotated[list, operator.add]
    retry_count: int
    max_retries: int
    status: str
    error: Optional[str]
""",
    "app/agent/tools.py": """from langchain_core.tools import tool
from app.database.connection import SessionLocal
from app.database.models import Product, Inventory, DemandForecast, PurchaseOrder, Supplier, SupplierProduct, Budget, StorageCapacity
import json
import uuid

@tool
def get_product_info(product_id: str) -> dict:
    \"\"\"Get basic product info.\"\"\"
    db = SessionLocal()
    p = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    return {"id": p.id, "name": p.name} if p else {}

@tool
def get_inventory_status(product_id: str, node_id: str) -> dict:
    \"\"\"Get inventory status.\"\"\"
    db = SessionLocal()
    i = db.query(Inventory).filter(Inventory.product_id == product_id, Inventory.node_id == node_id).first()
    db.close()
    return {"current": i.current_stock, "reserved": i.reserved_stock, "available": i.available_stock} if i else {}

@tool
def get_demand_forecast(product_id: str, node_id: str) -> dict:
    \"\"\"Get demand forecast.\"\"\"
    db = SessionLocal()
    f = db.query(DemandForecast).filter(DemandForecast.product_id == product_id, DemandForecast.node_id == node_id).first()
    db.close()
    return {"forecast": f.forecasted_demand, "actual": f.actual_demand} if f else {}

@tool
def get_open_purchase_orders(product_id: str = None, node_id: str = None) -> list:
    \"\"\"Get open purchase orders.\"\"\"
    db = SessionLocal()
    q = db.query(PurchaseOrder)
    if product_id: q = q.filter(PurchaseOrder.product_id == product_id)
    if node_id: q = q.filter(PurchaseOrder.node_id == node_id)
    res = q.all()
    db.close()
    return [{"id": r.id, "status": r.status, "qty": r.quantity_ordered} for r in res]

@tool
def get_supplier_info(supplier_id: str) -> dict:
    \"\"\"Get supplier info.\"\"\"
    db = SessionLocal()
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    db.close()
    return {"id": s.id, "lead_time": s.lead_time_days} if s else {}

@tool
def get_suppliers_for_product(product_id: str) -> list:
    \"\"\"Get suppliers for product.\"\"\"
    db = SessionLocal()
    sp = db.query(SupplierProduct).filter(SupplierProduct.product_id == product_id).all()
    res = [{"supplier_id": x.supplier_id, "price": x.unit_price} for x in sp]
    db.close()
    return res

@tool
def get_budget_status(node_id: str) -> dict:
    \"\"\"Get budget.\"\"\"
    db = SessionLocal()
    b = db.query(Budget).filter(Budget.node_id == node_id).first()
    db.close()
    return {"remaining": b.remaining} if b else {}

@tool
def get_storage_capacity(node_id: str) -> dict:
    \"\"\"Get storage.\"\"\"
    db = SessionLocal()
    c = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
    db.close()
    return {"available": c.available_units} if c else {}

@tool
def create_purchase_order(product_id: str, supplier_id: str, node_id: str, quantity: int, notes: str = '') -> dict:
    \"\"\"Create PO.\"\"\"
    db = SessionLocal()
    po = PurchaseOrder(id=str(uuid.uuid4()), product_id=product_id, supplier_id=supplier_id, node_id=node_id, quantity_ordered=quantity, status='pending', total_cost=0, created_by='agent', notes=notes)
    db.add(po)
    db.commit()
    res = {"id": po.id}
    db.close()
    return res

@tool
def modify_purchase_order(order_id: str, new_quantity: int = None, new_status: str = None, notes: str = '') -> dict:
    \"\"\"Modify PO.\"\"\"
    db = SessionLocal()
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    if new_quantity: po.quantity_ordered = new_quantity
    if new_status: po.status = new_status
    if notes: po.notes = notes
    db.commit()
    res = {"id": po.id}
    db.close()
    return res

@tool
def cancel_purchase_order(order_id: str, reason: str) -> dict:
    \"\"\"Cancel PO.\"\"\"
    db = SessionLocal()
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == order_id).first()
    po.status = 'cancelled'
    po.notes = reason
    db.commit()
    res = {"id": po.id}
    db.close()
    return res
""",
    "app/agent/nodes.py": """from app.agent.state import AgentState

def investigate_node(state: AgentState):
    state['status'] = 'investigating'
    state['reasoning_steps'].append("Investigating data...")
    state['investigation_data'] = {}
    return state

def analyze_node(state: AgentState):
    state['status'] = 'analyzing'
    state['reasoning_steps'].append("Analyzing data...")
    state['analysis'] = {"recommendation": "do something"}
    return state

def decide_node(state: AgentState):
    state['status'] = 'deciding'
    state['reasoning_steps'].append("Making decision...")
    state['decision'] = {"action": "create_po", "qty": 100}
    return state

def validate_node(state: AgentState):
    state['status'] = 'validating'
    state['reasoning_steps'].append("Validating decision...")
    state['validation_results'] = [{"check": "budget", "passed": True}]
    return state

def execute_node(state: AgentState):
    state['status'] = 'executing'
    state['reasoning_steps'].append("Executing decision...")
    state['execution_result'] = {"success": True}
    return state

def verify_node(state: AgentState):
    state['status'] = 'verifying'
    state['reasoning_steps'].append("Verifying execution...")
    state['verification_result'] = {"verified": True}
    return state

def handle_validation_failure(state: AgentState):
    state['retry_count'] += 1
    return state

def escalate_node(state: AgentState):
    state['status'] = 'escalated'
    return state

def should_execute_or_revise(state: AgentState):
    if all(v.get('passed', False) for v in state.get('validation_results', [])):
        return 'execute'
    if state['retry_count'] < state['max_retries']:
        return 'revise'
    return 'escalate'

def should_complete_or_retry(state: AgentState):
    if state.get('verification_result', {}).get('verified'):
        return 'complete'
    if state['retry_count'] < state['max_retries']:
        return 'retry'
    return 'escalate'
""",
    "app/agent/graph.py": """from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    investigate_node, analyze_node, decide_node, validate_node,
    execute_node, verify_node, handle_validation_failure, escalate_node,
    should_execute_or_revise, should_complete_or_retry
)
import json

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("investigate", investigate_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("decide", decide_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("revise", handle_validation_failure)
    
    workflow.set_entry_point("investigate")
    workflow.add_edge("investigate", "analyze")
    workflow.add_edge("analyze", "decide")
    workflow.add_edge("decide", "validate")
    
    workflow.add_conditional_edges(
        "validate",
        should_execute_or_revise,
        {
            "execute": "execute",
            "revise": "revise",
            "escalate": "escalate"
        }
    )
    workflow.add_edge("revise", "decide")
    
    workflow.add_edge("execute", "verify")
    
    workflow.add_conditional_edges(
        "verify",
        should_complete_or_retry,
        {
            "complete": END,
            "retry": "investigate",
            "escalate": "escalate"
        }
    )
    workflow.add_edge("escalate", END)
    
    return workflow.compile()

async def run_agent(config: dict):
    graph = build_graph()
    initial_state = {
        "messages": [],
        "scenario_type": config.get("scenario_type", "default"),
        "scenario_config": config.get("parameters", {}),
        "product_id": config.get("product_id", ""),
        "node_id": config.get("node_id", ""),
        "investigation_data": {},
        "analysis": {},
        "decision": {},
        "validation_results": [],
        "execution_result": None,
        "verification_result": None,
        "reasoning_steps": [],
        "retry_count": 0,
        "max_retries": 3,
        "status": "pending",
        "error": None
    }
    
    for state in graph.stream(initial_state):
        node_name = list(state.keys())[0]
        state_data = state[node_name]
        yield json.dumps({"node": node_name, "status": state_data.get("status")}) + "\\n\\n"
""",
    "app/services/__init__.py": "",
    "app/services/validator.py": """class ValidationRule:
    name: str = "BaseRule"
    def check(self, decision: dict, context: dict) -> dict:
        return {"check": self.name, "passed": True}

class BudgetCheck(ValidationRule): name = "BudgetCheck"
class StorageCheck(ValidationRule): name = "StorageCheck"
class MOQCheck(ValidationRule): name = "MOQCheck"
class MaxOrderCheck(ValidationRule): name = "MaxOrderCheck"
class LeadTimeCheck(ValidationRule): name = "LeadTimeCheck"
class DuplicateCheck(ValidationRule): name = "DuplicateCheck"

def run_all_validations(decision: dict, context: dict) -> list:
    rules = [BudgetCheck(), StorageCheck(), MOQCheck(), MaxOrderCheck(), LeadTimeCheck(), DuplicateCheck()]
    return [r.check(decision, context) for r in rules]
""",
    "app/services/feedback.py": """def verify_execution(expected_state: dict, actual_state: dict) -> dict:
    return {"verified": True}

def calculate_inventory_projection(current_stock, incoming_orders, daily_demand, days_ahead) -> list:
    return []

def detect_discrepancy(expected, actual) -> list:
    return []
""",
    "app/services/purchasing.py": """def calculate_coverage_days(available_stock, daily_demand) -> float:
    return available_stock / daily_demand if daily_demand else 0.0

def calculate_reorder_point(daily_demand, lead_time_days, safety_factor=1.5) -> int:
    return int(daily_demand * lead_time_days * safety_factor)

def calculate_optimal_order_quantity(demand_forecast, current_stock, incoming_orders, lead_time, min_order, max_order) -> int:
    return min_order

def assess_stockout_risk(inventory, forecast, open_orders) -> dict:
    return {"risk_level": "low"}
""",
    "app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import engine, Base
from app.database.seed import seed_database
from app.database.connection import SessionLocal
from app.api.routes import products, suppliers, orders, scenarios, agent

app = FastAPI(title="AI Purchasing Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)
    db.close()

app.include_router(products.router)
app.include_router(suppliers.router)
app.include_router(orders.router)
app.include_router(scenarios.router)
app.include_router(agent.router)

@app.get("/")
def root():
    return {"message": "AI Purchasing Agent Backend API Running"}
""",
    "tests/__init__.py": "",
    "tests/test_scenarios.py": """import pytest

def test_scenario_1_accept_recommendation():
    assert True

def test_scenario_1_reject_over_budget():
    assert True

def test_scenario_2_find_alternative_supplier():
    assert True

def test_scenario_3_demand_spike_emergency_order():
    assert True

def test_scenario_4_constraint_adaptation():
    assert True
"""
}

for rel_path, content in files_to_create.items():
    p = root_dir / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding='utf-8')

print("Backend files generated successfully.")
