from typing import TypedDict, Annotated, Optional
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
