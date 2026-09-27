from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime, date


class ScenarioRequest(BaseModel):
    scenario_id: str = "1"
    product_id: Optional[str] = None
    node_id: Optional[str] = None
    parameters: Optional[dict] = None


class ScenarioConfig(BaseModel):
    scenario_type: str = "recommendation_review"
    scenario_id: str = "1"
    product_id: str = "PRD-001"
    node_id: str = "NODE-NORTH"
    parameters: dict = {}


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sku: str
    category: str
    unit_cost: float
    selling_price: float
    min_stock_level: int
    max_stock_level: int
    storage_volume_per_unit: float


class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    product_id: str
    node_id: str
    current_stock: int
    reserved_stock: int
    available_stock: int


class SupplierResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    lead_time_days: int
    min_order_qty: int
    max_order_qty: int
    reliability_score: float
    active: bool


class PurchaseOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: str
    supplier_id: str
    node_id: str
    quantity_ordered: int
    quantity_confirmed: Optional[int] = None
    unit_price: float
    total_cost: float
    status: str
    expected_delivery: Optional[date] = None
    created_at: Optional[datetime] = None
    created_by: str
    notes: Optional[str] = None


class BudgetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    node_id: str
    category: str
    total_budget: float
    spent: float
    remaining: float


class StorageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    node_id: str
    total_capacity_units: int
    used_units: int
    available_units: int
