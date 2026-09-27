import json
import asyncio
from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.nodes import (
    investigate_node, analyze_node, decide_node, validate_node,
    execute_node, verify_node, handle_validation_failure, escalate_node,
    should_execute_or_revise, should_complete_or_retry
)


def build_graph():
    """Build the LangGraph state machine for the purchasing agent."""
    workflow = StateGraph(AgentState)
    
    # Add all nodes
    workflow.add_node("investigate", investigate_node)
    workflow.add_node("analyze", analyze_node)
    workflow.add_node("decide", decide_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("execute", execute_node)
    workflow.add_node("verify", verify_node)
    workflow.add_node("escalate", escalate_node)
    workflow.add_node("revise", handle_validation_failure)
    
    # Define edges
    workflow.set_entry_point("investigate")
    workflow.add_edge("investigate", "analyze")
    workflow.add_edge("analyze", "decide")
    workflow.add_edge("decide", "validate")
    
    # After validation: execute if passed, revise if failed, escalate if max retries
    workflow.add_conditional_edges(
        "validate",
        should_execute_or_revise,
        {
            "execute": "execute",
            "revise": "revise",
            "escalate": "escalate"
        }
    )
    
    # After revision, go back to decide
    workflow.add_edge("revise", "decide")
    
    # After execution, verify
    workflow.add_edge("execute", "verify")
    
    # After verification: complete if verified, retry if not, escalate if max retries
    workflow.add_conditional_edges(
        "verify",
        should_complete_or_retry,
        {
            "complete": END,
            "retry": "investigate",
            "escalate": "escalate"
        }
    )
    
    # Escalation ends the flow
    workflow.add_edge("escalate", END)
    
    return workflow.compile()


# Scenario configurations
SCENARIO_CONFIGS = {
    "1": {
        "id": "1",
        "name": "Purchase Recommendation Review",
        "description": "The purchasing system recommends buying 800 units of Organic Whole Milk. The agent investigates whether this recommendation should be accepted, modified, or rejected.",
        "type": "recommendation_review",
        "scenario_type": "recommendation_review",
        "product_id": "PRD-001",
        "node_id": "NODE-NORTH",
        "parameters": {
            "quantity": 800,
            "product_id": "PRD-001",
            "node_id": "NODE-NORTH"
        },
        "icon": "ClipboardCheck",
        "color": "indigo"
    },
    "2": {
        "id": "2",
        "name": "Supplier Partial Fulfillment",
        "description": "A purchase order for 500 units of Premium Orange Juice exists, but the supplier can only supply 250 units. The agent determines what should happen next.",
        "type": "supplier_partial",
        "scenario_type": "supplier_partial",
        "product_id": "PRD-004",
        "node_id": "NODE-NORTH",
        "parameters": {
            "po_id": "PO-2026-002",
            "product_id": "PRD-004",
            "node_id": "NODE-NORTH",
            "original_quantity": 500,
            "fulfilled_quantity": 250
        },
        "icon": "AlertTriangle",
        "color": "amber"
    },
    "3": {
        "id": "3",
        "name": "Demand Spike Response",
        "description": "Organic Bananas were expected to have 250 units/week demand, but actual sales are 750 units/week (3× forecast). The agent investigates and responds.",
        "type": "demand_spike",
        "scenario_type": "demand_spike",
        "product_id": "PRD-006",
        "node_id": "NODE-NORTH",
        "parameters": {
            "product_id": "PRD-006",
            "node_id": "NODE-NORTH",
            "quantity": 500
        },
        "icon": "TrendingUp",
        "color": "emerald"
    },
    "4": {
        "id": "4",
        "name": "Purchasing Constraint",
        "description": "The agent determines additional inventory is needed, but budget and storage constraints may prevent the ideal purchase from being executed.",
        "type": "constraint",
        "scenario_type": "constraint",
        "product_id": "PRD-001",
        "node_id": "NODE-NORTH",
        "parameters": {
            "product_id": "PRD-001",
            "node_id": "NODE-NORTH",
            "quantity": 1500
        },
        "icon": "ShieldAlert",
        "color": "rose"
    }
}


async def run_agent_stream(scenario_id: str):
    """Run the agent and yield SSE events for each state update."""
    config = SCENARIO_CONFIGS.get(scenario_id, SCENARIO_CONFIGS["1"])
    
    graph = build_graph()
    initial_state = {
        "messages": [],
        "scenario_type": config["scenario_type"],
        "scenario_config": config["parameters"],
        "product_id": config["product_id"],
        "node_id": config["node_id"],
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
    
    all_steps = []
    final_decision = None
    final_validations = []
    final_execution = None
    
    try:
        for state_update in graph.stream(initial_state):
            node_name = list(state_update.keys())[0]
            node_state = state_update[node_name]
            
            # Collect reasoning steps
            new_steps = node_state.get("reasoning_steps", [])
            for step in new_steps:
                all_steps.append(step)
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "step", "step": step})
                }
                await asyncio.sleep(0.3)  # Small delay for animation effect
            
            # Emit decision if available
            if "decision" in node_state and node_state["decision"]:
                final_decision = node_state["decision"]
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "decision", "decision": final_decision})
                }
            
            # Emit validation results
            if "validation_results" in node_state and node_state["validation_results"]:
                final_validations = node_state["validation_results"]
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "validation", "validations": final_validations})
                }
            
            # Emit execution result
            if "execution_result" in node_state and node_state["execution_result"]:
                final_execution = node_state["execution_result"]
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "execution", "execution": final_execution})
                }
            
            # Emit verification result
            if "verification_result" in node_state and node_state["verification_result"]:
                yield {
                    "event": "message",
                    "data": json.dumps({"type": "verification", "verification": node_state["verification_result"]})
                }
            
            await asyncio.sleep(0.1)
        
        # Send completion
        yield {
            "event": "message",
            "data": json.dumps({
                "type": "done",
                "summary": {
                    "total_steps": len(all_steps),
                    "decision": final_decision,
                    "validations_passed": sum(1 for v in final_validations if v.get("passed", False)),
                    "total_validations": len(final_validations),
                    "execution_success": final_execution.get("success", False) if final_execution else None
                }
            })
        }
    
    except Exception as e:
        yield {
            "event": "message",
            "data": json.dumps({"type": "error", "message": str(e)})
        }
