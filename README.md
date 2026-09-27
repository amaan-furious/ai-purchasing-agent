# 🤖 AI Purchasing Agent

> An intelligent full-stack AI agent that automates buyer purchasing decisions for quick-commerce operations. Built with FastAPI, LangGraph, React, and OpenAI.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Key Features](#key-features)
- [Scenarios](#scenarios)
- [Feedback Loop Design](#feedback-loop-design)
- [Tech Stack](#tech-stack)
- [Setup & Installation](#setup--installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing & Evaluation](#testing--evaluation)
- [Approach Description](#approach-description)
- [Decision Validation](#decision-validation)

---

## Overview

This AI Purchasing Agent is **not a chatbot** — it's a decision-making system that can:

1. **Investigate** purchasing situations by querying inventory, demand, suppliers, budgets, and constraints
2. **Analyze** the data to understand the current situation
3. **Make decisions** about whether to accept, modify, reject, or escalate purchase recommendations
4. **Validate** decisions against business rules before execution
5. **Execute** actions (create/modify/cancel purchase orders)
6. **Verify** outcomes and self-correct through a feedback loop

The system demonstrates all four required scenarios with a strong emphasis on the feedback loop and decision validation.

---

## Architecture

See [architecture.md](./architecture.md) for the complete architecture documentation.

### High-Level Flow

```
User triggers scenario
        │
        ▼
┌─────────────────┐     SSE Stream      ┌─────────────────┐
│  React Frontend │ ◄──────────────────► │ FastAPI Backend  │
│  (Dashboard)    │                      │  (REST + SSE)   │
└─────────────────┘                      └────────┬────────┘
                                                  │
                                         ┌────────┴────────┐
                                         │  LangGraph Agent │
                                         │  (State Machine) │
                                         └────────┬────────┘
                                                  │
                                    ┌─────────────┼─────────────┐
                                    │             │             │
                              ┌─────┴─────┐ ┌────┴────┐ ┌──────┴──────┐
                              │  SQLite   │ │ OpenAI  │ │ Validation  │
                              │  Database │ │  LLM    │ │   Engine    │
                              └───────────┘ └─────────┘ └─────────────┘
```

---

## Key Features

- 🧠 **Intelligent Agent** — LangGraph state machine with tool-calling capabilities
- 🔄 **Feedback Loop** — Pre-validation, execution, post-verification with automatic retry
- ✅ **Dual Validation** — Deterministic rule engine + LLM-powered analysis
- 📊 **Real-time Streaming** — Watch the agent think step-by-step via SSE
- 🎨 **Premium Dashboard** — Dark-mode, glassmorphism, animated React UI
- 📦 **Mock Data** — Realistic products, suppliers, inventory, forecasts, budgets
- 🧪 **Built-in Evaluation** — Automated test scenarios for all 4 use cases
- 🔧 **11 Agent Tools** — Database queries, PO management, supplier search

---

## Scenarios

### Scenario 1: Purchase Recommendation Review
The system recommends buying **800 units** of a product. The agent investigates current inventory, demand forecasts, open POs, supplier constraints, budget, and storage to determine whether to **accept, modify, reject, or investigate further**.

### Scenario 2: Supplier Partial Fulfillment
A PO for **500 units** exists, but the supplier can only supply **250 units**. The agent determines next steps: source from alternative suppliers, adjust the order, or escalate.

### Scenario 3: Demand Spike Response
Actual sales have increased **3× beyond forecast**. The agent evaluates whether existing POs and inventory are sufficient, and creates emergency orders if needed.

### Scenario 4: Purchasing Constraint
The agent needs to purchase additional inventory, but **budget or storage constraints** prevent the ideal purchase. The agent adapts its recommendation to work within constraints.

---

## Feedback Loop Design

This is the core differentiator of the system:

```
   Agent Decision
        │
        ▼
  ┌──────────────┐
  │ PRE-VALIDATE │ ─── FAIL ──→ Revise (up to 3 retries)
  │ (Rule Engine)│
  └──────┬───────┘
         │ PASS
         ▼
  ┌──────────────┐
  │   EXECUTE    │
  │  (Create PO) │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ POST-VERIFY  │ ─── FAIL ──→ Correct or Escalate
  │ (State Check)│
  └──────┬───────┘
         │ PASS
         ▼
     ✅ Complete
```

### Pre-Execution Validation Rules
- **Budget Check**: PO cost ≤ remaining budget
- **Storage Check**: PO quantity ≤ available storage capacity
- **MOQ Check**: Quantity ≥ supplier minimum order quantity
- **Max Order Check**: Quantity ≤ supplier maximum order quantity
- **Lead Time Check**: Delivery before projected stockout
- **Duplicate Check**: No existing active PO for same product/supplier

### Post-Execution Verification
- Re-queries database state after action
- Compares expected vs actual state
- Detects discrepancies
- Auto-corrects or escalates to human

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS + Framer Motion |
| Backend | FastAPI (Python 3.10+) |
| AI Agent | LangGraph + LangChain |
| LLM | OpenAI GPT-4o-mini / GPT-4o |
| Database | SQLite + SQLAlchemy |
| Streaming | Server-Sent Events (SSE) |
| Testing | Pytest |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm 9+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ai-purchasing-agent.git
cd ai-purchasing-agent
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

### 4. Environment Configuration

Create a `.env` file in the `backend/` directory:

```env
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./purchasing.db
```

---

## Running the Application

### Start the Backend

```bash
cd backend
# Activate virtual environment first
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
Interactive API docs at `http://localhost:8000/docs`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The dashboard will be available at `http://localhost:3000`

### Quick Start (Both)

Open two terminals:

```bash
# Terminal 1: Backend
cd backend && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

## API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products |
| GET | `/api/inventory/{node_id}` | Get inventory for a node |
| GET | `/api/suppliers` | List all suppliers |
| GET | `/api/orders` | List purchase orders |
| GET | `/api/scenarios` | List available scenarios |
| POST | `/api/scenarios/{id}/run` | Run a scenario (SSE stream) |
| POST | `/api/scenarios/{id}/reset` | Reset scenario data |
| GET | `/api/agent/decisions` | List past agent decisions |

Full interactive documentation available at `http://localhost:8000/docs` when the server is running.

---

## Testing & Evaluation

See [evaluation.md](./evaluation.md) for the complete evaluation approach.

### Run Tests

```bash
cd backend
pytest tests/test_scenarios.py -v
```

### What We Test

| Aspect | How We Verify |
|--------|--------------|
| Data Gathering | Agent queries all relevant data sources |
| Correct Calculations | Coverage days, costs, quantities are accurate |
| Constraint Compliance | Budget, storage, MOQ all satisfied |
| Appropriate Decision | Decision type matches the situation |
| Clear Reasoning | Agent explains its decision |
| Validation | All deterministic rules pass |
| Execution | Actions successfully completed |
| Post-Verification | Resulting state matches expectations |
| Error Handling | Failures handled gracefully |

---

## Approach Description

### Problem Breakdown

I approached this as a **decision automation system**, not a chatbot. The key insight is that purchasing decisions follow a structured investigation → analysis → decision → validation → execution → verification cycle.

### Design Decisions

1. **LangGraph over simple LLM calls**: The purchasing workflow requires state management, conditional branching, and feedback loops. LangGraph provides this natively as a state machine.

2. **Deterministic validation + LLM reasoning**: The agent uses the LLM for understanding and reasoning, but critical constraint checks (budget, storage, MOQ) are deterministic Python functions. This prevents the LLM from "hallucinating" that a purchase is affordable when it isn't.

3. **Tool-calling architecture**: The agent has specific tools for querying data and taking actions, rather than having direct database access. This makes the system auditable and controllable.

4. **SSE streaming**: Real-time display of the agent's reasoning process. Users can see exactly what the agent is investigating, what data it found, and how it reached its decision.

5. **Mock data tells a story**: The seed data is carefully crafted so each scenario naturally arises from the data state. Scenario 3's demand spike, for example, is visible in the forecast vs actual demand data.

### What Information the Agent Needs
- Current inventory levels (available, reserved)
- Demand forecasts (expected vs actual)
- Existing open purchase orders
- Supplier details (lead times, MOQs, reliability, pricing)
- Budget constraints
- Storage capacity constraints

### How Decisions Are Made
1. Calculate coverage days: `available_stock / daily_demand`
2. Factor in incoming orders: `available + incoming_POs`
3. Identify gaps: `projected_demand - projected_supply`
4. Check constraints: budget, storage, MOQ, lead time
5. Make decision: accept/modify/reject/escalate

### When Human Approval Is Appropriate
- When constraints cannot be resolved (e.g., no budget and no alternative)
- When risk is high (large orders, unreliable suppliers)
- When the situation is ambiguous (conflicting signals)
- When the agent has exhausted its retry attempts

---

## Decision Validation

### How We Validate Agent Decisions

**Pre-Execution (Preventive)**:
- 6 deterministic validation rules run before any action
- Each rule produces a pass/fail result with explanation
- Failed validations trigger decision revision

**Post-Execution (Detective)**:
- System re-queries database after action
- Compares expected state vs actual state
- Detects discrepancies (wrong quantity, missing PO, etc.)
- Triggers auto-correction or escalation

**What Happens When Initial Action Doesn't Work**:
1. The verification step detects the failure
2. The agent receives the failure context
3. The agent revises its approach (up to 3 retries)
4. If still failing, escalates to human with full context

This dual validation approach ensures decisions are both **preventively validated** (before execution) and **retrospectively verified** (after execution), creating a robust feedback loop.

---

## License

MIT
