export interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  unit_cost: number;
  selling_price: number;
  price?: number;
  min_stock_level: number;
  max_stock_level: number;
  storage_volume_per_unit: number;
  margin?: number;
  margin_pct?: number;
}

export interface InventoryItem {
  product_id: string;
  product_name: string;
  category: string;
  node_id: string;
  current_stock: number;
  reserved_stock: number;
  available_stock: number;
  min_stock_level: number;
  status: 'HEALTHY' | 'CRITICAL';
}

export interface Supplier {
  id: string;
  name: string;
  lead_time_days: number;
  min_order_qty: number;
  max_order_qty: number;
  reliability_score: number;
  reliabilityScore?: number;
  active: boolean;
  products_supplied?: string[];
}

export interface PurchaseOrder {
  id: string;
  product_id: string;
  productId?: string;
  supplier_id: string;
  node_id: string;
  quantity_ordered: number;
  quantity?: number;
  quantity_confirmed?: number;
  unit_price: number;
  total_cost: number;
  status: 'pending' | 'confirmed' | 'partial' | 'delivered' | 'cancelled' | 'rejected' | 'approved';
  expected_delivery: string;
  created_at: string;
  created_by: string;
  notes?: string;
}

export interface DemandForecast {
  product_id: string;
  product_name: string;
  node_id: string;
  period_start: string;
  period_end: string;
  forecasted_demand: number;
  actual_demand: number | null;
  confidence: number;
  has_anomaly: boolean;
}

export interface Budget {
  node_id: string;
  category: string;
  total_budget: number;
  total?: number;
  spent: number;
  utilized?: number;
  remaining: number;
  utilization_pct: number;
}

export interface StorageCapacity {
  node_id: string;
  total_capacity_units: number;
  totalVolume?: number;
  used_units: number;
  utilizedVolume?: number;
  available_units: number;
  utilization_pct: number;
}

export interface Scenario {
  id: string;
  name: string;
  description: string;
  type: string;
  product_id: string;
  node_id: string;
  icon: string;
  color: string;
}

export interface ScenarioConfig {
  [key: string]: any;
}

export interface ReasoningStep {
  id: string;
  type: 'investigate' | 'tool_call' | 'analyze' | 'decide' | 'validate' | 'execute' | 'verify' | 'error' | 'escalate';
  title: string;
  description: string;
  timestamp: string;
  status: 'active' | 'completed' | 'failed';
  data?: any;
}

export interface ValidationResult {
  rule_name?: string;
  ruleName?: string;
  ruleId?: string;
  passed: boolean;
  details: string;
}

export interface ExecutionResult {
  success: boolean;
  actionTaken?: string;
  details?: string;
  actions?: Array<{
    tool: string;
    args: any;
    result: string;
  }>;
}

export interface VerificationResult {
  verified: boolean;
  checks: Array<{
    check: string;
    passed: boolean;
    detail: string;
  }>;
  discrepancies: string;
  summary: string;
}

export interface AgentDecision {
  id: number;
  scenario_type?: string;
  scenarioId?: string;
  productId?: string;
  product_id?: string;
  decision_type?: 'accept' | 'modify' | 'reject' | 'escalate';
  decision?: string;
  confidenceScore?: number;
  modifiedQuantity?: number;
  originalQuantity?: number;
  reasoning?: string[];
  original_recommendation?: any;
  final_decision?: any;
  validation_results?: ValidationResult[];
  execution_result?: ExecutionResult | null;
  status?: string;
  created_at?: string;
  timestamp?: string;
}

export interface SSEEvent {
  type: 'step' | 'decision' | 'validation' | 'execution' | 'verification' | 'done' | 'error';
  step?: ReasoningStep;
  decision?: any;
  validations?: ValidationResult[];
  execution?: ExecutionResult;
  verification?: VerificationResult;
  message?: string;
  summary?: any;
}
