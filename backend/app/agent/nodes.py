import json
import os
from datetime import datetime
from typing import Literal

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.state import AgentState
from app.agent.tools import (
    get_product_info, get_inventory_status, get_demand_forecast,
    get_open_purchase_orders, get_supplier_info, get_suppliers_for_product,
    get_budget_status, get_storage_capacity, create_purchase_order,
    modify_purchase_order, cancel_purchase_order
)
from app.agent.prompts import MAIN_SYSTEM_PROMPT, SCENARIO_PROMPTS
from app.services.validator import run_all_validations
from app.services.feedback import verify_execution, build_context_for_validation
from app.config import settings


def _get_llm(with_tools=True):
    """Create LLM instance with or without tools."""
    all_tools = [
        get_product_info, get_inventory_status, get_demand_forecast,
        get_open_purchase_orders, get_supplier_info, get_suppliers_for_product,
        get_budget_status, get_storage_capacity, create_purchase_order,
        modify_purchase_order, cancel_purchase_order
    ]
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            temperature=0.1
        )
        if with_tools:
            llm = llm.bind_tools(all_tools)
        return llm
    except Exception:
        return None


def _make_reasoning_step(step_type: str, title: str, description: str, data=None, status="completed"):
    """Create a structured reasoning step for the frontend timeline."""
    return {
        "id": f"{step_type}-{datetime.utcnow().timestamp()}",
        "type": step_type,
        "title": title,
        "description": description,
        "timestamp": datetime.utcnow().isoformat(),
        "status": status,
        "data": data
    }


def investigate_node(state: AgentState) -> dict:
    """Investigation node: Uses LLM with tools to gather all relevant data."""
    scenario_type = state["scenario_type"]
    config = state["scenario_config"]
    product_id = state["product_id"]
    node_id = state["node_id"]
    
    steps = [_make_reasoning_step(
        "investigate", 
        "Starting Investigation",
        f"Gathering data for {scenario_type} scenario: product {product_id} at {node_id}",
        status="active"
    )]
    
    # Build scenario-specific prompt
    fmt_kwargs = {"product_id": product_id, "node_id": node_id, **config}
    scenario_prompt = SCENARIO_PROMPTS.get(scenario_type, "").format(**fmt_kwargs)
    
    llm = _get_llm(with_tools=True)
    
    investigation_data = {}
    
    if llm:
        messages = [
            SystemMessage(content=MAIN_SYSTEM_PROMPT),
            HumanMessage(content=f"{scenario_prompt}\n\nStart by investigating ALL relevant data sources. Query inventory, demand, open POs, suppliers, budget, and storage. Do not skip any data source.")
        ]
        
        # Run tool-calling loop
        max_iterations = 15
        for i in range(max_iterations):
            response = llm.invoke(messages)
            messages.append(response)
            
            if not response.tool_calls:
                break
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                # Execute tool
                tool_map = {
                    "get_product_info": get_product_info,
                    "get_inventory_status": get_inventory_status,
                    "get_demand_forecast": get_demand_forecast,
                    "get_open_purchase_orders": get_open_purchase_orders,
                    "get_supplier_info": get_supplier_info,
                    "get_suppliers_for_product": get_suppliers_for_product,
                    "get_budget_status": get_budget_status,
                    "get_storage_capacity": get_storage_capacity,
                }
                
                if tool_name in tool_map:
                    result = tool_map[tool_name].invoke(tool_args)
                    investigation_data[tool_name] = result
                    
                    steps.append(_make_reasoning_step(
                        "tool_call",
                        f"Queried: {tool_name.replace('_', ' ').title()}",
                        str(result)[:300],
                        data={"tool": tool_name, "args": tool_args}
                    ))
                    
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
        
        # Extract the LLM's investigation summary
        if messages and hasattr(messages[-1], 'content') and messages[-1].content:
            investigation_data["llm_summary"] = messages[-1].content
    else:
        # Fallback: directly query all data sources without LLM
        steps.append(_make_reasoning_step(
            "investigate", "Using Rule-Based Investigation",
            "LLM not available. Querying all data sources directly."
        ))
        investigation_data["product"] = get_product_info.invoke({"product_id": product_id})
        investigation_data["inventory"] = get_inventory_status.invoke({"product_id": product_id, "node_id": node_id})
        investigation_data["forecast"] = get_demand_forecast.invoke({"product_id": product_id, "node_id": node_id})
        investigation_data["open_pos"] = get_open_purchase_orders.invoke({"product_id": product_id, "node_id": node_id})
        investigation_data["suppliers"] = get_suppliers_for_product.invoke({"product_id": product_id})
        investigation_data["budget"] = get_budget_status.invoke({"node_id": node_id})
        investigation_data["storage"] = get_storage_capacity.invoke({"node_id": node_id})
    
    steps.append(_make_reasoning_step(
        "investigate", "Investigation Complete",
        f"Gathered data from {len(investigation_data)} sources."
    ))
    
    return {
        "investigation_data": investigation_data,
        "reasoning_steps": steps,
        "status": "investigated",
        "messages": messages if llm else []
    }


def analyze_node(state: AgentState) -> dict:
    """Analysis node: LLM analyzes collected data and formulates assessment."""
    steps = [_make_reasoning_step(
        "analyze", "Analyzing Data",
        "Synthesizing investigation results to form assessment.",
        status="active"
    )]
    
    investigation = state["investigation_data"]
    messages = list(state.get("messages", []))
    llm = _get_llm(with_tools=False)
    
    analysis = {}
    
    if llm and messages:
        messages.append(HumanMessage(content=(
            "Based on the data you've gathered, provide your analysis. Include:\n"
            "1. Current coverage days (available stock / daily demand)\n"
            "2. Projected coverage including incoming POs\n"
            "3. Supply gap analysis\n"
            "4. Constraint assessment (budget, storage, supplier)\n"
            "5. Risk assessment\n"
            "6. Your initial recommendation\n\n"
            "Format your analysis clearly with numbers and calculations."
        )))
        response = llm.invoke(messages)
        messages.append(response)
        analysis["llm_analysis"] = response.content
    else:
        # Rule-based analysis fallback
        analysis["llm_analysis"] = "Rule-based analysis: Data collected, proceeding with deterministic decision."
    
    steps.append(_make_reasoning_step(
        "analyze", "Analysis Complete",
        analysis.get("llm_analysis", "")[:500]
    ))
    
    return {
        "analysis": analysis,
        "reasoning_steps": steps,
        "status": "analyzed",
        "messages": messages
    }


def decide_node(state: AgentState) -> dict:
    """Decision node: LLM makes the final purchasing decision."""
    steps = [_make_reasoning_step(
        "decide", "Making Decision",
        "Formulating purchasing decision based on analysis.",
        status="active"
    )]
    
    messages = list(state.get("messages", []))
    config = state["scenario_config"]
    llm = _get_llm(with_tools=False)
    
    decision = {}
    
    if llm and messages:
        messages.append(HumanMessage(content=(
            "Based on your analysis, make your FINAL decision. Respond in this EXACT JSON format:\n"
            "{\n"
            '  "decision_type": "accept" | "modify" | "reject" | "escalate",\n'
            '  "reasoning": ["reason 1", "reason 2", ...],\n'
            '  "recommended_quantity": <number or null>,\n'
            '  "recommended_supplier_id": "<supplier_id or null>",\n'
            '  "confidence_score": <0.0-1.0>,\n'
            '  "key_factors": ["factor 1", "factor 2", ...],\n'
            '  "risks": ["risk 1", "risk 2", ...],\n'
            '  "action_plan": "Description of what action to take"\n'
            "}\n\n"
            "Respond ONLY with the JSON, no other text."
        )))
        response = llm.invoke(messages)
        messages.append(response)
        
        # Parse the decision JSON
        try:
            content = response.content.strip()
            if content.startswith("```"):
                content = content.split("\n", 1)[1].rsplit("```", 1)[0]
            decision = json.loads(content)
        except json.JSONDecodeError:
            decision = {
                "decision_type": "modify",
                "reasoning": [response.content[:500]],
                "recommended_quantity": config.get("quantity", 0),
                "recommended_supplier_id": None,
                "confidence_score": 0.7,
                "key_factors": ["LLM response could not be parsed as JSON"],
                "risks": ["Decision may need manual review"],
                "action_plan": response.content[:300]
            }
    else:
        # Rule-based decision fallback: dynamically calculate feasible quantity based on storage & budget
        from app.database.connection import SessionLocal
        from app.database.models import StorageCapacity, Budget, SupplierProduct as SP
        db = SessionLocal()
        
        target_qty = config.get("quantity", 800)
        node_id = state["node_id"]
        product_id = state["product_id"]
        
        # Check storage
        storage = db.query(StorageCapacity).filter(StorageCapacity.node_id == node_id).first()
        avail_storage = storage.available_units if storage else 1000
        
        # Check primary supplier and budget
        sp = db.query(SP).filter(SP.product_id == product_id).order_by(SP.priority).first()
        supp_id = sp.supplier_id if sp else "SUP-001"
        unit_price = sp.unit_price if sp else 2.5
        
        budget = db.query(Budget).filter(Budget.node_id == node_id).first()
        max_budget_qty = int(budget.remaining // unit_price) if (budget and unit_price) else 1000
        
        db.close()
        
        # Cap quantity to feasible limit
        feasible_qty = min(target_qty, avail_storage, max_budget_qty)
        
        decision_type = "accept" if feasible_qty == target_qty else "modify"
        
        decision = {
            "decision_type": decision_type,
            "reasoning": [
                f"Evaluated target quantity {target_qty}.",
                f"Adjusted to feasible quantity {feasible_qty} based on available storage ({avail_storage} units) and budget constraints."
            ],
            "recommended_quantity": feasible_qty,
            "recommended_supplier_id": supp_id,
            "confidence_score": 0.85,
            "key_factors": [
                f"Available Storage: {avail_storage} units",
                f"Budget-capped max: {max_budget_qty} units",
                f"Primary Supplier: {supp_id}"
            ],
            "risks": ["Rule-based adaptation executed"],
            "action_plan": f"Create purchase order for {feasible_qty} units with supplier {supp_id}"
        }
    
    # Ensure supplier_id is resolved if missing or None
    if not decision.get("recommended_supplier_id"):
        from app.database.connection import SessionLocal
        from app.database.models import SupplierProduct as SP
        db = SessionLocal()
        try:
            sp = db.query(SP).filter(SP.product_id == state["product_id"]).order_by(SP.priority).first()
            if sp:
                decision["recommended_supplier_id"] = sp.supplier_id
        finally:
            db.close()

    steps.append(_make_reasoning_step(
        "decide", f"Decision: {decision.get('decision_type', 'unknown').upper()}",
        f"Confidence: {decision.get('confidence_score', 0)*100:.0f}% | " + 
        "; ".join(decision.get('key_factors', [])[:3]),
        data=decision
    ))
    
    return {
        "decision": decision,
        "reasoning_steps": steps,
        "status": "decided",
        "messages": messages
    }


def validate_node(state: AgentState) -> dict:
    """Validation node: Runs DETERMINISTIC business rule validation."""
    steps = [_make_reasoning_step(
        "validate", "Running Validation Rules",
        "Checking decision against business constraints.",
        status="active"
    )]
    
    decision = state["decision"]
    product_id = state["product_id"]
    node_id = state["node_id"]
    
    context = build_context_for_validation(product_id, node_id)
    validation_results = run_all_validations(decision, context)
    
    all_passed = all(v["passed"] for v in validation_results)
    passed_count = sum(1 for v in validation_results if v["passed"])
    total_count = len(validation_results)
    
    for v in validation_results:
        steps.append(_make_reasoning_step(
            "validate",
            f"{'✅' if v['passed'] else '❌'} {v['rule_name']}",
            v["details"],
            data=v
        ))
    
    steps.append(_make_reasoning_step(
        "validate",
        f"Validation {'PASSED' if all_passed else 'FAILED'}",
        f"{passed_count}/{total_count} checks passed.",
        data={"all_passed": all_passed, "results": validation_results}
    ))
    
    return {
        "validation_results": validation_results,
        "reasoning_steps": steps,
        "status": "validated" if all_passed else "validation_failed"
    }


def execute_node(state: AgentState) -> dict:
    """Execution node: Executes the validated decision."""
    decision = state["decision"]
    product_id = state["product_id"]
    node_id = state["node_id"]
    config = state["scenario_config"]
    scenario_type = state["scenario_type"]
    
    steps = [_make_reasoning_step(
        "execute", "Executing Decision",
        f"Taking action: {decision.get('action_plan', 'Execute purchase')}",
        status="active"
    )]
    
    execution_result = {"success": False, "actions": []}
    
    messages = list(state.get("messages", []))
    llm = _get_llm(with_tools=True)
    
    if llm and messages:
        messages.append(HumanMessage(content=(
            f"Now execute your decision. Your decision was: {json.dumps(decision)}\n\n"
            "Use the appropriate tools to take action:\n"
            "- Use create_purchase_order to create new POs\n"
            "- Use modify_purchase_order to modify existing POs\n"
            "- Use cancel_purchase_order to cancel POs\n\n"
            "Execute the action now."
        )))
        
        max_iterations = 10
        for i in range(max_iterations):
            response = llm.invoke(messages)
            messages.append(response)
            
            if not response.tool_calls:
                break
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                action_tools = {
                    "create_purchase_order": create_purchase_order,
                    "modify_purchase_order": modify_purchase_order,
                    "cancel_purchase_order": cancel_purchase_order,
                }
                
                if tool_name in action_tools:
                    result = action_tools[tool_name].invoke(tool_args)
                    execution_result["actions"].append({
                        "tool": tool_name,
                        "args": tool_args,
                        "result": str(result)
                    })
                    execution_result["success"] = "✅" in str(result)
                    
                    steps.append(_make_reasoning_step(
                        "execute",
                        f"Executed: {tool_name.replace('_', ' ').title()}",
                        str(result)[:300],
                        data={"tool": tool_name, "args": tool_args}
                    ))
                    
                    from langchain_core.messages import ToolMessage
                    messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
    else:
        # Rule-based execution fallback
        qty = decision.get("recommended_quantity", config.get("quantity", 100))
        supplier_id = decision.get("recommended_supplier_id")
        
        if not supplier_id:
            suppliers_info = get_suppliers_for_product.invoke({"product_id": product_id})
            # Find primary supplier from the data
            from app.database.connection import SessionLocal
            from app.database.models import SupplierProduct as SP
            db = SessionLocal()
            sp = db.query(SP).filter(SP.product_id == product_id).order_by(SP.priority).first()
            supplier_id = sp.supplier_id if sp else "SUP-001"
            db.close()
        
        if decision.get("decision_type") in ["accept", "modify"]:
            result = create_purchase_order.invoke({
                "product_id": product_id,
                "supplier_id": supplier_id,
                "node_id": node_id,
                "quantity": qty,
                "notes": f"Agent decision: {decision.get('decision_type')}"
            })
            execution_result = {"success": "✅" in str(result), "actions": [{"result": str(result)}]}
            
            steps.append(_make_reasoning_step(
                "execute", "Purchase Order Created",
                str(result)[:300]
            ))
    
    steps.append(_make_reasoning_step(
        "execute",
        f"Execution {'Successful' if execution_result['success'] else 'Failed'}",
        f"{len(execution_result['actions'])} action(s) taken."
    ))
    
    return {
        "execution_result": execution_result,
        "reasoning_steps": steps,
        "status": "executed",
        "messages": messages
    }


def verify_node(state: AgentState) -> dict:
    """Verification node: Post-execution verification (feedback loop)."""
    steps = [_make_reasoning_step(
        "verify", "Post-Execution Verification",
        "Verifying that the execution produced the expected results.",
        status="active"
    )]
    
    product_id = state["product_id"]
    node_id = state["node_id"]
    decision = state["decision"]
    execution_result = state["execution_result"]
    
    verification = verify_execution(
        product_id=product_id,
        node_id=node_id,
        decision=decision,
        execution_result=execution_result
    )
    
    if verification["verified"]:
        steps.append(_make_reasoning_step(
            "verify", "✅ Verification Passed",
            verification.get("summary", "All post-execution checks passed."),
            data=verification
        ))
    else:
        steps.append(_make_reasoning_step(
            "error", "❌ Verification Failed",
            verification.get("discrepancies", "Unexpected state after execution."),
            data=verification
        ))
    
    # Save decision to database
    from app.database.connection import SessionLocal
    from app.database.models import AgentDecision
    db = SessionLocal()
    try:
        agent_decision = AgentDecision(
            scenario_type=state["scenario_type"],
            decision_type=decision.get("decision_type", "unknown"),
            original_recommendation=state["scenario_config"],
            agent_analysis=state.get("analysis", {}),
            final_decision=decision,
            validation_results=state.get("validation_results", []),
            execution_result=execution_result,
            feedback_loop_log=verification,
            status="verified" if verification["verified"] else "verification_failed"
        )
        db.add(agent_decision)
        db.commit()
    except Exception as e:
        db.rollback()
    finally:
        db.close()
    
    return {
        "verification_result": verification,
        "reasoning_steps": steps,
        "status": "verified" if verification["verified"] else "verification_failed"
    }


def handle_validation_failure(state: AgentState) -> dict:
    """Handle validation failure by revising the decision."""
    retry_count = state.get("retry_count", 0) + 1
    failed_rules = [v for v in state.get("validation_results", []) if not v.get("passed", True)]
    
    steps = [_make_reasoning_step(
        "error", f"Revising Decision (Attempt {retry_count})",
        f"Validation failed on: {', '.join(v.get('rule_name', '') for v in failed_rules)}. Revising...",
        data={"retry_count": retry_count, "failed_rules": failed_rules}
    )]
    
    # Inject failure context into messages so LLM can revise
    messages = list(state.get("messages", []))
    failure_detail = "\n".join([f"- {v.get('rule_name')}: {v.get('details')}" for v in failed_rules])
    messages.append(HumanMessage(content=(
        f"Your previous decision FAILED validation on these rules:\n{failure_detail}\n\n"
        f"Please revise your decision to respect these constraints. This is attempt {retry_count} of {state.get('max_retries', 3)}."
    )))
    
    return {
        "retry_count": retry_count,
        "reasoning_steps": steps,
        "messages": messages,
        "status": "revising"
    }


def escalate_node(state: AgentState) -> dict:
    """Escalate to human when agent cannot resolve the situation."""
    decision = state.get("decision", {})
    failed_validations = [v for v in state.get("validation_results", []) if not v.get("passed", True)]
    
    escalation_reason = (
        f"Agent could not resolve the purchasing decision after {state.get('retry_count', 0)} attempts. "
        f"Failed validations: {', '.join(v.get('rule_name', '') for v in failed_validations)}. "
        f"Original decision: {decision.get('decision_type', 'unknown')} for {decision.get('recommended_quantity', 'N/A')} units."
    )
    
    steps = [_make_reasoning_step(
        "escalate", "🚨 Escalated to Human Buyer",
        escalation_reason,
        data={
            "retry_count": state.get("retry_count", 0),
            "failed_validations": failed_validations,
            "original_decision": decision
        }
    )]
    
    # Save escalation decision
    from app.database.connection import SessionLocal
    from app.database.models import AgentDecision
    db = SessionLocal()
    try:
        agent_decision = AgentDecision(
            scenario_type=state["scenario_type"],
            decision_type="escalate",
            original_recommendation=state["scenario_config"],
            agent_analysis=state.get("analysis", {}),
            final_decision={"decision_type": "escalate", "reason": escalation_reason},
            validation_results=state.get("validation_results", []),
            execution_result=None,
            feedback_loop_log={"escalated": True, "reason": escalation_reason},
            status="escalated"
        )
        db.add(agent_decision)
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    
    return {
        "reasoning_steps": steps,
        "status": "escalated"
    }


def should_execute_or_revise(state: AgentState) -> Literal["execute", "revise", "escalate"]:
    """Route after validation: execute if passed, revise if failed, escalate if max retries."""
    validations = state.get("validation_results", [])
    all_passed = all(v.get("passed", False) for v in validations)
    
    if all_passed:
        return "execute"
    
    if state.get("retry_count", 0) < state.get("max_retries", 3):
        return "revise"
    
    return "escalate"


def should_complete_or_retry(state: AgentState) -> Literal["complete", "retry", "escalate"]:
    """Route after verification: complete if verified, retry if not, escalate if max retries."""
    verification = state.get("verification_result", {})
    
    if verification.get("verified", False):
        return "complete"
    
    if state.get("retry_count", 0) < state.get("max_retries", 3):
        return "retry"
    
    return "escalate"
