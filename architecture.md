# Architecture — AI Purchasing Agent

## System Overview

The AI Purchasing Agent is a full-stack application that automates buyer purchasing decisions for a quick-commerce company. It uses an AI agent powered by LangGraph to investigate purchasing situations, make data-driven decisions, validate them against business constraints, execute actions, and verify outcomes through a robust feedback loop.

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│  ┌──────────┐ ┌──────────────┐ ┌────────────┐ ┌─────────────┐  │
│  │Dashboard │ │Scenario      │ │ Agent      │ │  Data       │  │
│  │  KPIs    │ │ Runner       │ │ Timeline   │ │  Explorer   │  │
│  └──────────┘ └──────────────┘ └────────────┘ └─────────────┘  │
│                           │ SSE Stream                          │
└───────────────────────────┼─────────────────────────────────────┘
                            │ HTTP / SSE
┌───────────────────────────┼─────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  ┌────────────────────────┼────────────────────────────────┐    │
│  │              REST API Layer                             │    │
│  │  /api/products  /api/suppliers  /api/orders             │    │
│  │  /api/scenarios  /api/agent                             │    │
│  └────────────────────────┼────────────────────────────────┘    │
│                           │                                     │
│  ┌────────────────────────┼────────────────────────────────┐    │
│  │           AI AGENT (LangGraph State Machine)            │    │
│  │                                                         │    │
│  │  ┌───────────┐  ┌─────────┐  ┌────────┐  ┌──────────┐  │    │
│  │  │Investigate│→ │ Analyze │→ │ Decide │→ │ Validate │  │    │
│  │  └───────────┘  └─────────┘  └────────┘  └────┬─────┘  │    │
│  │                                                │        │    │
│  │                              ┌─────────────────┤        │    │
│  │                              │ Pass            │ Fail   │    │
│  │                              ▼                 ▼        │    │
│  │                        ┌──────────┐    ┌──────────┐     │    │
│  │                        │ Execute  │    │  Revise  │     │    │
│  │                        └────┬─────┘    └──────────┘     │    │
│  │                             │                           │    │
│  │                        ┌────┴─────┐                     │    │
│  │                        │  Verify  │ ← FEEDBACK LOOP     │    │
│  │                        └────┬─────┘                     │    │
│  │                             │                           │    │
│  │                    ┌────────┤────────┐                  │    │
│  │                    │ OK     │ Fail   │ Escalate         │    │
│  │                    ▼        ▼        ▼                  │    │
│  │               ┌────────┐ ┌──────┐ ┌──────────┐         │    │
│  │               │Complete│ │Retry │ │ Escalate │         │    │
│  │               └────────┘ └──────┘ └──────────┘         │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                 │
│  ┌──────────────────────┐  ┌────────────────────────────┐      │
│  │  Validation Engine   │  │   Feedback Loop Engine     │      │
│  │  • Budget Check      │  │   • Pre-execution verify   │      │
│  │  • Storage Check     │  │   • Post-execution verify  │      │
│  │  • MOQ Check         │  │   • State comparison       │      │
│  │  • Lead Time Check   │  │   • Discrepancy detection  │      │
│  │  • Duplicate Check   │  │   • Auto-correction        │      │
│  └──────────────────────┘  └────────────────────────────┘      │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Agent Tools (LangChain @tool)              │    │
│  │  get_product_info    get_inventory_status               │    │
│  │  get_demand_forecast get_open_purchase_orders           │    │
│  │  get_supplier_info   get_suppliers_for_product          │    │
│  │  get_budget_status   get_storage_capacity               │    │
│  │  create_purchase_order modify_purchase_order            │    │
│  │  cancel_purchase_order                                  │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────┐
│                     DATABASE (SQLite)                            │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌─────────────────┐   │
│  │ Products │ │ Inventory │ │Suppliers │ │ Purchase Orders │   │
│  └──────────┘ └───────────┘ └──────────┘ └─────────────────┘   │
│  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌─────────────────┐   │
│  │Forecasts │ │  Budgets  │ │ Storage  │ │ Agent Decisions │   │
│  └──────────┘ └───────────┘ └──────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Agent Decision Flow

The agent follows a structured decision-making process:

### 1. Investigation Phase
The agent queries all relevant data sources:
- Current inventory levels at the fulfillment node
- Demand forecasts (expected vs actual)
- Existing open purchase orders
- Supplier information (lead times, MOQs, reliability)
- Budget availability
- Storage capacity

### 2. Analysis Phase
The agent synthesizes the collected data:
- Calculates coverage days (how long current stock lasts)
- Identifies supply gaps
- Evaluates supplier options
- Assesses risk levels

### 3. Decision Phase
Based on analysis, the agent determines the appropriate action:
- **Accept** — The recommendation is sound
- **Modify** — Adjust quantity, supplier, or timing
- **Reject** — The recommendation doesn't make sense given current data
- **Escalate** — The situation requires human judgment

### 4. Pre-Execution Validation (Deterministic)
Before executing any action, deterministic business rules validate the decision:
- Budget constraint: `total_cost ≤ remaining_budget`
- Storage constraint: `quantity ≤ available_storage`
- MOQ constraint: `quantity ≥ supplier_min_order_qty`
- Max order constraint: `quantity ≤ supplier_max_order_qty`
- Lead time constraint: `delivery_date < projected_stockout_date`
- Duplicate check: no active PO for same product/supplier

### 5. Execution Phase
The validated decision is executed:
- Create new purchase orders
- Modify existing purchase orders
- Cancel purchase orders
- Split orders across suppliers

### 6. Post-Execution Verification (Feedback Loop)
After execution, the system verifies the outcome:
- Re-queries database state
- Compares expected state vs actual state
- Checks that PO was created/modified correctly
- Verifies inventory projections still meet demand
- If discrepancy detected: retry or escalate

## Feedback Loop Design

```
   Decision Made
        │
        ▼
  ┌──────────────┐
  │ Pre-Execution│──── FAIL ──→ Revise Decision (up to 3 retries)
  │  Validation  │
  └──────┬───────┘
         │ PASS
         ▼
  ┌──────────────┐
  │   Execute    │
  │   Action     │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │Post-Execution│──── FAIL ──→ Corrective Action or Escalate
  │ Verification │
  └──────┬───────┘
         │ PASS
         ▼
     ✅ Complete
```

### Why This Matters
1. **Pre-validation catches invalid decisions** before they cause problems
2. **Post-verification catches unexpected outcomes** (e.g., supplier API rejects order)
3. **Retry logic allows self-correction** without human intervention
4. **Escalation ensures humans are involved** when the agent can't resolve issues
5. **Full audit trail** of every decision, validation, and outcome

## Data Model

### Core Entities
- **Product**: Items the company sells (SKU, pricing, stock levels)
- **InventoryNode**: Fulfillment centers/warehouses
- **Inventory**: Stock levels per product per node
- **Supplier**: External suppliers with lead times, MOQs, reliability
- **SupplierProduct**: Which suppliers carry which products (pricing, priority)
- **PurchaseOrder**: Orders placed to suppliers
- **DemandForecast**: Expected vs actual demand
- **Budget**: Financial constraints per node
- **StorageCapacity**: Physical constraints per node
- **AgentDecision**: Audit log of all agent decisions

## Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| Frontend | React + Vite + TypeScript | Fast development, excellent DX, SPA perfect for dashboard |
| Styling | Tailwind CSS + Framer Motion | Premium dark UI with smooth animations |
| Backend | FastAPI (Python) | Async support, auto-docs, Pydantic integration |
| AI Agent | LangGraph + LangChain | Stateful agent graph with feedback loops, tool calling |
| LLM | OpenAI GPT-4o-mini / GPT-4o | Best tool-calling support, structured outputs |
| Database | SQLite + SQLAlchemy | Zero-config, perfect for demo, full relational support |
| Streaming | Server-Sent Events (SSE) | Real-time agent reasoning display in frontend |
