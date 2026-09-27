# Evaluation — Test Scenarios & Validation Approach

## Overview

This document describes how we evaluate whether the AI Purchasing Agent makes appropriate decisions. Our evaluation approach focuses on three dimensions:

1. **Decision Correctness** — Did the agent make the right call?
2. **Process Quality** — Did the agent gather the right information and follow a sound process?
3. **Constraint Compliance** — Did the agent respect all business constraints?

---

## Test Scenarios

### Scenario 1: Purchase Recommendation Review

#### Test 1.1: Accept with Modification
**Setup:**
- Product: Organic Whole Milk 1L (PRD-001)
- System recommends: 800 units
- Current inventory: 450 units (400 available)
- Weekly demand forecast: 600 units
- Existing PO: 300 units arriving in 2 days
- Budget remaining: $18,000
- Storage available: 1,200 units

**Expected Agent Behavior:**
1. ✅ Agent queries inventory, demand, open POs, supplier info, budget, storage
2. ✅ Agent calculates: available stock (400) + incoming PO (300) = 700 units
3. ✅ Agent calculates: weekly demand is 600, so 700 covers ~8.2 days
4. ✅ Agent considers whether 800 additional units are needed
5. ✅ Agent checks budget: 800 × $2.50 = $2,000 ≤ $18,000 ✓
6. ✅ Agent checks storage: 800 ≤ 1,200 available ✓
7. ✅ Agent may accept or modify the quantity based on coverage target
8. ✅ Decision is validated against all business rules
9. ✅ PO is created and post-verified

**Evaluation Criteria:**
- Did the agent consider existing open POs (not just current stock)?
- Did the agent calculate coverage days correctly?
- Did the decision respect budget and storage constraints?
- Was the reasoning clearly explained?

#### Test 1.2: Reject — Over Budget
**Setup:** Same as 1.1 but budget remaining is only $1,500 (below the $2,000 needed for 800 units)

**Expected Agent Behavior:**
1. ✅ Agent detects budget constraint
2. ✅ Agent either rejects or modifies quantity to fit budget (max ~600 units at $2.50)
3. ✅ Agent explains the budget limitation
4. ✅ Pre-validation catches the budget violation if agent tries to order 800

---

### Scenario 2: Supplier Partial Fulfillment

#### Test 2.1: Find Alternative Supplier
**Setup:**
- Product: Premium Orange Juice 1L (PRD-004)
- Original PO: 500 units from Coastal Distributors (SUP-002)
- Supplier can fulfill: 250 units only
- Current inventory: 500 available
- Weekly demand: 400 units
- Alternative suppliers available

**Expected Agent Behavior:**
1. ✅ Agent assesses the shortfall: need 250 more units
2. ✅ Agent checks if current inventory + 250 covers demand
3. ✅ Agent searches for alternative suppliers
4. ✅ Agent finds alternative and creates supplementary PO
5. ✅ Agent modifies original PO to 250 units
6. ✅ Post-verification confirms both POs total 500 units

**Evaluation Criteria:**
- Did the agent properly calculate the shortfall?
- Did the agent look for alternatives before escalating?
- Were both POs verified to cover the demand gap?

#### Test 2.2: No Alternative — Escalate
**Setup:** Same as 2.1 but no alternative suppliers carry the product

**Expected Agent Behavior:**
1. ✅ Agent searches for alternatives, finds none
2. ✅ Agent evaluates if 250 units + existing inventory is sufficient
3. ✅ Agent escalates to human with clear options and recommendation

---

### Scenario 3: Demand Spike

#### Test 3.1: Emergency Purchase Order
**Setup:**
- Product: Organic Bananas (PRD-006)
- Forecast: 250 units/week
- Actual demand: 750 units/week (3× spike)
- Current inventory: 160 available
- Existing PO: 200 units arriving in 3 days
- Supplier lead time: 3 days

**Expected Agent Behavior:**
1. ✅ Agent detects demand anomaly (actual 3× forecast)
2. ✅ Agent calculates: 160 available + 200 incoming = 360 units
3. ✅ Agent calculates: at 750/week rate, 360 covers only ~3.4 days
4. ✅ Agent determines emergency purchase is needed
5. ✅ Agent creates emergency PO for additional units
6. ✅ Agent considers whether spike is temporary or sustained
7. ✅ Post-verification confirms new inventory projection

**Evaluation Criteria:**
- Did the agent recognize the demand anomaly?
- Did the agent properly calculate the supply gap?
- Was the emergency order sized appropriately?
- Did the agent consider the nature of the demand spike?

---

### Scenario 4: Purchasing Constraint

#### Test 4.1: Storage Constraint Adaptation
**Setup:**
- Product: Any product where agent determines 1,500 units needed
- Storage available: only 1,200 units
- Budget: sufficient

**Expected Agent Behavior:**
1. ✅ Agent identifies the need for 1,500 units
2. ✅ Pre-validation catches storage constraint violation
3. ✅ Agent adapts order to 1,200 units (max storage)
4. ✅ Agent may suggest staggered deliveries or storage optimization
5. ✅ Modified order passes validation and is executed

#### Test 4.2: Budget Constraint Adaptation
**Setup:**
- Agent wants to order quantity that exceeds budget
- Multiple constraints interact

**Expected Agent Behavior:**
1. ✅ Agent identifies budget limitation
2. ✅ Agent calculates maximum affordable quantity
3. ✅ Agent adapts order or finds cheaper supplier
4. ✅ Agent explains the trade-off clearly

---

## Evaluation Methodology

### Automated Validation
Each test runs the agent and checks:

```python
def evaluate_decision(result):
    checks = {
        'data_gathering': check_all_data_sources_queried(result),
        'constraint_compliance': check_constraints_respected(result),
        'decision_reasoning': check_reasoning_provided(result),
        'validation_passed': check_pre_validation(result),
        'execution_success': check_execution_completed(result),
        'verification_passed': check_post_verification(result),
        'feedback_loop_worked': check_feedback_loop(result),
    }
    return all(checks.values()), checks
```

### Decision Quality Criteria

| Criteria | How We Check |
|----------|-------------|
| **Information Gathering** | Agent queried all relevant data sources (inventory, demand, suppliers, budget, storage, open POs) |
| **Correct Calculation** | Coverage days, costs, and quantities are mathematically correct |
| **Constraint Respect** | Budget, storage, MOQ, and lead time constraints are all satisfied |
| **Appropriate Action** | The decision type (accept/modify/reject/escalate) matches the situation |
| **Clear Reasoning** | The agent explained why it made its decision |
| **Validation Passed** | All deterministic validation rules passed |
| **Execution Success** | The action was successfully executed (PO created/modified) |
| **Post-Verification** | The resulting state matches expectations |
| **Error Handling** | When something fails, the agent handles it gracefully |

### Feedback Loop Validation

The feedback loop is validated by intentionally creating scenarios where:

1. **Pre-validation catches errors**: Agent tries to exceed budget → validation fails → agent revises
2. **Post-verification catches discrepancies**: PO created with wrong quantity → verification detects → agent corrects
3. **Escalation works**: After max retries → agent escalates to human with clear explanation
4. **Retry succeeds**: First attempt fails due to constraint → second attempt adapts and succeeds

### Running the Evaluation

```bash
# Run all scenario tests
cd backend
pytest tests/test_scenarios.py -v

# Run with detailed output
pytest tests/test_scenarios.py -v --tb=long -s
```

---

## What Makes This Evaluation Approach Strong

1. **Not just checking outputs** — We verify the entire process (data gathering → analysis → decision → validation → execution → verification)
2. **Deterministic validation** — Business rules are checked mathematically, not relying on LLM judgment for constraint compliance
3. **Feedback loop testing** — We specifically test error scenarios to prove the feedback loop works
4. **Dual validation** — Both pre-execution (preventing bad decisions) and post-execution (catching unexpected outcomes)
5. **Transparency** — Every agent decision is logged with full reasoning, making it auditable
6. **Constraint-aware** — Every test explicitly verifies that business constraints were respected
